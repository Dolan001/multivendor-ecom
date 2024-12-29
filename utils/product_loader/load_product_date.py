import time
from random import randint

import requests
from django.db import transaction
from rest_framework import exceptions

from product.models.models import (
    Bleach,
    Brand,
    Category,
    Characteristic,
    Color,
    ColorWay,
    Composition,
    ConceptViewImage,
    DryCleaning,
    Drying,
    Fabric,
    Ironing,
    Laundry,
    Pattern,
    PhotographedImage,
    Product,
    ProductColorway,
    ProductDesign,
    ProductDesignImage,
    ProductDesignOption,
    ProductMainImage,
    ProductOption,
    ProductOptionPrice,
    ProductSize,
    ProductSizePrice,
    Specification,
    Washing,
    Wring,
)
from utils.helper.load_fabric_data import get_image


class ProductLoader:
    def send_url_request(self, url, count=0):
        if not url:
            return {"error": "URL is required"}
        response = requests.get(url)
        if response.status_code != 200:
            while count < 1:
                count += 1
                return self.send_url_request(url, count)

            return False

        print(f"Requesting {url} | Status Code: {response.status_code}")
        return response.json()

    def get_design(self, design_ids: list = None) -> list:
        data = self.send_url_request(
            "http://falette-atelier-backend-alb-prod-1264321608.ap-northeast-2.elb.amazonaws.com/designs"
        )
        if design_ids:
            filtered_design = []
            for design in data:
                if design.get("id") in design_ids:
                    filtered_design.append(design)
            return filtered_design
        return data

    def get_fabrics(self, design_category, fabric_ids: list = None) -> list:
        data = self.send_url_request(
            "http://falette-atelier-backend-alb-prod-1264321608.ap-northeast-2.elb.amazonaws.com/fabrics"
        )
        # print(fabric_ids)
        if fabric_ids:

            response_fabrics = []
            for fabric in data:
                if fabric.get("id") in fabric_ids:
                    response_fabrics.append(fabric)

            return response_fabrics
        return data

    def get_render_images(self, *, design_id, febric_id, colorway_id) -> list:
        data = self.send_url_request(
            f"http://falette-atelier-backend-alb-prod-1264321608.ap-northeast-2.elb.amazonaws.com/designs/{design_id}/rendered-images?fabricId={febric_id}"
        )
        if not data:
            return data
        filtered_colorway = []
        for colorway in data["colorWayImages"]:
            if colorway["colorWayId"] == colorway_id:
                filtered_colorway.append(colorway)
        data["colorWayImages"] = filtered_colorway
        return data

    def get_product_prices(self, design, fabric):
        data = self.send_url_request(
            f"http://falette-atelier-backend-alb-prod-1264321608.ap-northeast-2.elb.amazonaws.com/designs/{design.design_id}/price?fabricId={fabric.fabric_id}"
        )
        # print(data)
        return data

    def get_products(self, fabrics_ids: list = None, design_ids: list = None):
        designs = self.get_design(design_ids)  # get all design
        if not designs:
            return
        product_list = []
        count = 1
        for design in designs:
            design_id = design.get("id")  # get design id
            design_category = design["productCategory"]  # get design category
            fabrics = self.get_fabrics(design_category, fabrics_ids)  # get all fabrics
            if not fabrics:
                continue
            product_count = 0
            for fabric in fabrics:
                # if product_count > 4:
                #     print(f"{product_count-1} Products added for ", fabric["id"])
                #     break

                fabric_id = fabric["id"]  # get fabric id
                colorways = fabric["colorWays"]  # get all colorways
                valid_colorways = []
                for colorway in colorways:
                    colorway_id = colorway["id"]
                    render_images = self.get_render_images(
                        design_id=design_id,
                        febric_id=fabric_id,
                        colorway_id=colorway_id,
                    )
                    if not render_images:
                        continue
                    colorway["renderImages"] = render_images
                    valid_colorways.append(colorway)

                fabric["colorWays"] = valid_colorways

                product = {
                    "design": design,
                    "fabric": fabric,
                }
                # create product object into database
                self.create_product(product, count)
                product_list.append(product)
                count += 1
                time.sleep(5)

        return product_list

    @transaction.atomic
    def create_product(self, product_data, count=1):
        # create product category
        try:
            # with transaction.atomic():
            category, created = Category.objects.get_or_create(
                title=product_data.get("design").get("productCategory"),
                category_type="SUB",
            )
            # product_sizes = self.product_sizes_add(category)
            design = self.product_design(product_data, category)
            # create product fabric
            fabric = self.fabric_data(product_data.get("fabric"))

            # product create
            if len(product_data.get("fabric").get("colorWays")) > 0:
                thumbnail_url = (
                    product_data.get("fabric")
                    .get("colorWays")[0]
                    .get("renderImages")
                    .get("colorWayImages")[0]
                    .get("productThumbnailImage")
                    .get("url")
                )
                product = self.product_create(design, fabric, category, thumbnail_url)

                # colorway
                colorways = product_data.get("fabric").get("colorWays", None)
                colorways = self.product_colorway(colorways, fabric, product)
                print(f"{count} : {product.name} created successfully")
                return product
        except Exception as e:
            print(
                f"{count} : {product_data.get('design').get('productCategory')} failed"
            )
            return False

    def product_create(self, design, fabric, category, thumbnail_url):

        get_size_price = self.get_product_prices(design, fabric)
        product_sizes = get_size_price.get("sizeOptionPrices")
        product_options = get_size_price.get("designOptionPrices")

        product_name = f"{fabric.name}"
        product, _ = Product.objects.get_or_create(
            name=product_name, fabric=fabric, category=category, product_design=design
        )
        # product.name = product_name
        product.thumbnail = get_image(thumbnail_url, thumbnail_url.split("/")[-1])
        product.save(update_fields=["thumbnail"])

        self.add_product_size_prices(category, product, product_sizes)
        self.add_product_option_prices(category, product, product_options)
        return product

    def add_product_size_prices(self, category, product, product_sizes):
        existing_size = []
        for product_size in product_sizes:
            try:
                size, created = ProductSize.objects.get_or_create(
                    category=category, size=product_size.get("name").strip()
                )
                product_size_price, created = ProductSizePrice.objects.get_or_create(
                    product=product, size=size
                )
                product_size_price.price = product_size.get("price")
                product_size_price.is_default = product_size.get("isDefault")
                product_size_price.save()
                existing_size.append(product_size_price.id)

                # if product_size.get("isDefault"):
                #     print("isDefault true")
                #     product.price = product_size.get("price")
                #     product.save()

            except:
                continue
        ProductSizePrice.objects.filter(product=product).exclude(
            id__in=existing_size
        ).delete()  # delete unused sizes

    def add_product_option_prices(self, category, product, product_options):
        existing_option = []
        for product_option in product_options:
            try:
                option, created = ProductOption.objects.get_or_create(
                    category=category,
                    name=product_option.get("name").strip(),
                    caption=product_option.get("name").strip(),
                )
                product_option_price, created = (
                    ProductOptionPrice.objects.get_or_create(
                        product=product, option=option
                    )
                )
                product_option_price.price = product_option.get("price")
                product_option_price.is_default = product_option.get("isDefault")
                product_option_price.save()
                existing_option.append(product_option_price.id)

            except:
                continue
        ProductOptionPrice.objects.filter(product=product).exclude(
            id__in=existing_option
        ).delete()  # delete unused options

    def product_design(self, product_data, category):

        design, _ = ProductDesign.objects.get_or_create(
            name=product_data.get("design").get("name"),
            category=category,
            defaults={"design_id": product_data.get("design").get("id")},
        )
        # design.design_id = product_data.get("design").get("id")
        # design.save()
        design_images = product_data.get("design").get("productImages")

        if len(design_images) > 0:
            # remove previous images
            ProductDesignImage.objects.filter(product_design=design).delete()
            design_bulk_object = []
            for design_image in design_images:
                get_design_image = get_image(
                    design_image["url"], design_image["url"].split("/")[-1]
                )
                design_bulk_object.append(
                    ProductDesignImage(
                        product_design=design,
                        image=get_design_image,
                        caption=design_image["caption"],
                    )
                )
            product_design_images = ProductDesignImage.objects.bulk_create(
                design_bulk_object
            )
        return design

    def fabric_data(
        self,
        fabric_obj,
    ):
        if brand := fabric_obj.get("brand"):
            brand, _ = Brand.objects.get_or_create(
                name=brand.get("name"), nationality=brand.get("nationality")
            )
            fabric, _ = Fabric.objects.get_or_create(
                fabric_id=fabric_obj.get("id").strip(),
                name=fabric_obj.get("name").strip(),
                brand=brand,
                defaults={
                    "name": fabric_obj.get("name").strip(),
                    "brand": brand,
                },
            )

            fabric.description = fabric_obj.get("description")
            if len(fabric_obj.get("colorWays")) > 0:
                fabric.thumbnail = get_image(
                    fabric_obj.get("colorWays")[0].get("thumbnailUrl"),
                    fabric_obj.get("colorWays")[0].get("thumbnailUrl").split("/")[-1],
                )
                fabric.save(update_fields=["description", "thumbnail"])
        else:
            raise exceptions.NotFound("Brand is required")
        # =============Fabric================
        patterns = fabric_obj.get("patterns", None)
        characteristics = fabric_obj.get("characteristics", None)
        available_categories = fabric_obj.get("availableProductCategories", None)

        if len(patterns) > 0:
            pattern_objects = []
            for value in patterns:
                pattern, _ = Pattern.objects.get_or_create(name=value)
                pattern_objects.append(pattern)
            fabric.patterns.set(pattern_objects)  # assign to fabrics patterns

        if len(characteristics) > 0:
            characteristics_objects = []
            for value in characteristics:
                characteristic, _ = Characteristic.objects.get_or_create(name=value)
                characteristics_objects.append(characteristic)
            fabric.characteristics.set(
                characteristics_objects
            )  # assign to fabrics patterns

        if len(available_categories) > 0:
            category_objects = []
            for value in available_categories:
                category, _ = Category.objects.get_or_create(
                    title=value, category_type="SUB"
                )
                category_objects.append(category)
            fabric.category.set(category_objects)  # assign to fabrics patterns

        # =============Fabric options ================
        compositions = fabric_obj.get("compositions", None)
        specification = fabric_obj.get("specification", None)
        laundry = fabric_obj.get("laundryInformation", None)

        if compositions:
            for value in compositions:
                composition, _ = Composition.objects.get_or_create(
                    material=value.get("material"),
                    ratio=value.get("ratio"),
                    fabric=fabric,
                )
        if specification:
            thickness = specification.get("thickness")
            transparency = specification.get("transparencyLevel")
            weight = specification.get("weight")
            specification, _ = Specification.objects.get_or_create(
                thickness=thickness,
                transparency_level=transparency,
                weight=weight,
                fabric=fabric,
            )
        if laundry:
            washing_method = laundry.get("washingMethod")
            dry_cleaning_method = laundry.get("dryCleaningMethod")
            wring_method = laundry.get("wringMethod")
            bleach_method = laundry.get("bleachMethod")
            ironing_method = laundry.get("ironingMethod")
            drying_method = laundry.get("dryingMethod")
            # get laundry objects
            washing = Washing.objects.filter(id=washing_method).first()
            dry_cleaning = DryCleaning.objects.filter(id=dry_cleaning_method).first()
            wring = Wring.objects.filter(id=wring_method).first()
            bleach = Bleach.objects.filter(id=bleach_method).first()
            ironing = Ironing.objects.filter(id=ironing_method).first()
            drying = Drying.objects.filter(id=drying_method).first()
            # create laundry objects
            laundry = Laundry.objects.get_or_create(
                washing=washing,
                dry_cleaning=dry_cleaning,
                wring=wring,
                bleach=bleach,
                ironing=ironing,
                drying=drying,
                fabric=fabric,
            )

        return fabric

    def product_colorway(self, product_colorway_obj, fabric, product):
        for item in product_colorway_obj:
            colorway, _ = ColorWay.objects.get_or_create(
                name=item.get("name"), fabric=fabric
            )

            colors = Color.objects.filter(name__in=item.get("colors"))
            colorway.colors.set(colors)
            colorway.save()
            colorway.thumbnail = get_image(
                item.get("thumbnailUrl"), item.get("thumbnailUrl").split("/")[-1]
            )
            colorway.representative_color = item.get("representativeColor")
            colorway.save(update_fields=["thumbnail", "representative_color"])
            # real fabric colorway images
            real_fabric_colorway_images = item.get("realFabricColorwayImages")
            PhotographedImage.objects.filter(color_way=colorway).delete()
            for url in real_fabric_colorway_images:
                colorway_image = get_image(url, colorway.name)
                photo_graphed_image = PhotographedImage.objects.create(
                    color_way=colorway, image=colorway_image
                )

            # product colorway

            product_colorway, _ = ProductColorway.objects.get_or_create(
                product=product, colorway=colorway
            )

            # product colorway images
            render_images = item.get("renderImages").get("colorWayImages")[0]
            self.product_colorway_render_images(render_images, product_colorway)

        return colorway

    def product_colorway_render_images(self, render_images, product_colorway):
        product_colorway.thumbnail = get_image(
            render_images.get("productThumbnailImage").get("url"),
            render_images.get("productThumbnailImage").get("url").split("/")[-1],
        )
        product_colorway.save(update_fields=["thumbnail"])

        # product concept images
        colorway_concept_images = render_images.get("productConceptImages", None)
        product_main_images = render_images.get("productMainImages", None)
        product_option_images = render_images.get("productOptionImages", None)
        if len(colorway_concept_images) > 0:
            ConceptViewImage.objects.filter(
                product_colorway=product_colorway
            ).delete()  # delete previous images
            for concept_image in colorway_concept_images:
                image = get_image(
                    concept_image.get("url"), concept_image.get("url").split("/")[-1]
                )
                concept_view_image = ConceptViewImage.objects.create(
                    product_colorway=product_colorway,
                    image=image,
                    caption=concept_image.get("caption"),
                )
        if len(product_option_images) > 0:
            ProductDesignOption.objects.filter(
                product_colorway=product_colorway
            ).delete()
            for option_image in product_option_images:
                image = get_image(
                    option_image.get("url"), option_image.get("url").split("/")[-1]
                )
                option_image = ProductDesignOption.objects.create(
                    product_colorway=product_colorway,
                    image=image,
                    caption=option_image.get("caption"),
                    price=float(randint(10, 100)),
                )
        if len(product_main_images) > 0:
            ProductMainImage.objects.filter(product_colorway=product_colorway).delete()
            for main_image in product_main_images:
                image = get_image(
                    main_image.get("url"), main_image.get("url").split("/")[-1]
                )
                main_image = ProductMainImage.objects.create(
                    product_colorway=product_colorway,
                    image=image,
                    caption=main_image.get("caption"),
                )
        return True

    def product_sizes_add(self, category=None):
        size_values = {
            "바란스 커튼": ["S(80x145)", "M(100x145)"],
            "쿠션 커버": ["S(40x40)", "M(45x45)", "L(50x50)"],
            "방석 커버": ["S(40x40)", "M(45x45)", "L(50x50)"],
            "테이블 보": [
                "2인(130x130)",
                "4인(180x130)",
                "6인(220x130)",
                "8인(240x130)",
            ],
            "테이블 러너": [
                "2인(130x130)",
                "4인(180x130)",
                "6인(220x130)",
                "8인(240x130)",
            ],
            "테이블 매트": ["S(10x10)", "M(20x20)"],
            "코스터 & 팟홀더": ["S(80x145)", "M(100x145)"],
            "파우치": ["XS", "S", "M", "L"],
            "에코백": ["S", "M"],
        }
        default_sizes = ["S", "M", "L"]

        # Determine categories to process
        categories = [category] if category else Category.objects.all()

        for cat in categories:
            # Get the size list for the category, default to `default_sizes` if not found
            sizes = size_values.get(cat.title, default_sizes)

            # Use `get_or_create` to add or update sizes with random price
            for size in sizes:
                obj, created = ProductSize.objects.get_or_create(
                    category=cat, size=size
                )
                if created:
                    # Set a random price only if it's a new entry
                    obj.price = float(randint(10, 100))
                    obj.save(update_fields=["price"])
        return True

    # def load_accessories(self, ):

    # @transaction.atomic
    # def create_product(self, product_data):
    #     category, created = Category.objects.get_or_create(
    #         title=product_data["design"]["productCategory"], category_type="SUB"
    #     )
    #
    #     design, design_created = ProductDesign.objects.get_or_create(
    #         name=product_data["design"].get("name"), category=category
    #     )
    #     if design_created:
    #         design_images = product_data["design"]["productImages"]
    #         if len(design_images) > 0:
    #             for design_image in design_images:
    #                 get_design_image = get_image(
    #                     design_image["url"], design_image["url"].split("/")[-1]
    #                 )
    #                 ProductDesignImage.objects.create(
    #                     product_design=design,
    #                     image=get_design_image,
    #                     caption=design_image["caption"],
    #                 )
    #
    #     # print(type(product_data["fabric"]))
    #
    #     # print("start creating product..................")
    #     fabric = fabric_data([product_data["fabric"]])
    #     product_name = (
    #         f"{product_data['design']['name']} {product_data['fabric']['name']}"
    #     )
    #     # create product instance
    #     thumbnail_url = product_data["fabric"]["colorWays"][0]["renderImages"][
    #         "colorWayImages"
    #     ][0]["productMainImages"][0]["url"]
    #     product_images = get_image(thumbnail_url, thumbnail_url.split("/")[-1])
    #
    #     size_values = {
    #         "바란스 커튼": ["S(80x145)", "M(100x145)"],
    #         "쿠션 커버": ["S(40x40)", "M(45x45)", "L(50x50)"],
    #         "방석 커버": ["S(40x40)", "M(45x45)", "L(50x50)"],
    #         "테이블 보": [
    #             "2인(130x130)",
    #             "4인(180x130)",
    #             "6인(220x130)",
    #             "8인(240x130)",
    #         ],
    #         "테이블 러너": [
    #             "2인(130x130)",
    #             "4인(180x130)",
    #             "6인(220x130)",
    #             "8인(240x130)",
    #         ],
    #         "테이블 매트": ["S(10x10)", "M(20x20)"],
    #         "코스터 & 팟홀더": ["S(80x145)", "M(100x145)"],
    #         "파우치": ["XS", "S", "M", "L"],
    #         "에코백": ["S", "M"],
    #     }
    #
    #     product, created = Product.objects.get_or_create(
    #         name=product_name, category=category, fabric=fabric, product_design=design
    #     )
    #     product.thumbnail = product_images
    #     product.description = product_data["fabric"]["description"]
    #     if product.price == float(0):
    #         product.price = float(10000)
    #     product.save()
    #
    #     if created:
    #         # creating product size
    #         # sizes = size_values.get(category.title, ["S", "M", "L"])
    #         # for size in sizes:
    #         #     s, created = ProductSize.objects.get_or_create(
    #         #         category=category.title, size=size, price=float(randint(10, 100))
    #         #     )
    #
    #         # product color way
    #         color_ways = product_data["fabric"]["colorWays"]
    #
    #         for color_way in color_ways:
    #             color_way_images = color_way["renderImages"]["colorWayImages"]
    #             # product_colorway_images = color_way["renderImages"]["productColorwayImages"]
    #             # print(color_way_images)
    #             for color_way_image in color_way_images:
    #                 product_main_images = color_way_image["productMainImages"]
    #                 color_way_concept_images = color_way_image["productConceptImages"]
    #                 product_option_images = color_way_image["productOptionImages"]
    #                 # print(color_way, "color_way")
    #                 color_way = ColorWay.objects.filter(
    #                     fabric=fabric,
    #                     name=color_way.get("name"),
    #                 ).last()
    #
    #                 product_colorway, created = ProductColorway.objects.get_or_create(
    #                     product=product, colorway=color_way
    #                 )
    #
    #                 for color_way_concept_image in color_way_concept_images:
    #                     image = get_image(
    #                         color_way_concept_image["url"],
    #                         color_way_concept_image["url"].split("/")[-1],
    #                     )
    #                     concept_view_image, created = (
    #                         ConceptViewImage.objects.get_or_create(
    #                             product_colorway=product_colorway,
    #                             image=image,
    #                             caption=color_way_concept_image.get("caption"),
    #                         )
    #                     )
    #
    #                 for product_option_image in product_option_images:
    #                     image = get_image(
    #                         product_option_image["url"],
    #                         product_option_image["url"].split("/")[-1],
    #                     )
    #                     option_image, created = (
    #                         ProductDesignOption.objects.get_or_create(
    #                             product_colorway=product_colorway,
    #                             image=image,
    #                             caption=product_option_image.get("caption"),
    #                             price=float(randint(10, 100)),
    #                         )
    #                     )
    #
    #                 for product_main_image in product_main_images:
    #                     image = get_image(
    #                         product_main_image["url"],
    #                         product_main_image["url"].split("/")[-1],
    #                     )
    #                     main_image, created = ProductMainImage.objects.get_or_create(
    #                         product_colorway=product_colorway,
    #                         image=image,
    #                         caption=product_main_image["caption"],
    #                     )
    #     # except Exception as e:
    #     #     print(product_data["design"]["productCategory"], "failed")
    #
    #     # for product_colorway_image in product_colorway_images:
    #     #     image = get_image(
    #     #         product_colorway_image["url"],
    #     #         product_colorway_image["url"].split("/")[-1],
    #     #     )
    #     #     colorway_image, created = ProductColorwayImage.objects.get_or_create(
    #     #         product=product,
    #     #         image=image,
    #     #         caption=product_colorway_image["caption"],
    #     #     )
