from django.views import generic
from django.shortcuts import redirect,render

from product.models import Variant,ProductVariantPrice,ProductVariant,Product
from django.db.models import Count

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import json

@method_decorator(csrf_exempt, name='dispatch')
class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def post(self, request, *args, **kwargs):
        
        data = request.body.decode('utf-8')
        body = json.loads(data)

        print(body.keys())
        title = body["title"]
        sku = body["sku"]
        description = body["description"]

        # product_image = request.body.get("product_image")
        product_variant = body["product_variant"]
        product_variant_prices =body["product_variant_prices"]
        

      
        print(product_variant_prices)

        
        new_product=Product.objects.create(title=title,sku=sku,description=description)
        new_product.save()

        
        for option in product_variant:
            
            for i in range( len(option['tags'])):
                print(option['tags'][i],option['option'])
                variant= Variant.objects.get(id=option['option'])
                new_product_variant=ProductVariant.objects.create(variant_title=option['tags'][i],product=new_product,variant=variant)
                new_product_variant.save()
            
        

        # for product_variant_price in product_variant_prices:
        #     product_variant=product_variant_price['title'].split('/')
        #     product_variant.pop()
           
        #     print(product_variant)
    
        #     if product_variant[0]:
        #         product_variant_one=ProductVariant.objects.get(product=Product.objects.get(id=new_product.id),variant_title=product_variant[0])
        #     if product_variant[1]:
        #         product_variant_two=ProductVariant.objects.get(product=Product.objects.get(id=new_product.id),variant_title=product_variant[1])
        #     if product_variant[2]:
        #         product_variant_three=ProductVariant.objects.get(product=Product.objects.get(id=new_product.id),variant_title=product_variant[2])

        #     new_product_variant_price=ProductVariantPrice.objects.create(product_variant_one=product_variant_one,product_variant_two=product_variant_two,product_variant_three=product_variant_three,price=100,stock=100,product=Product.objects.get(id=new_product.id))
        #     new_product_variant_price.save()

        #new_product_variant=ProductVariant.objects.create(variant_title=option['tags'][i],product=new_product,variant)


        return render(self.template_name, {"message": "Product created successfully"})

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter().values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context

""" 
Product List View

 """

class ListProductView(generic.ListView):
    template_name = 'products/list.html'
    paginate_by = 2
    model = Product
    context_object_name = 'products'
    
    def get_queryset(self):
        object_list = Product.objects.prefetch_related('productvariant_set').all()

        title = self.request.GET.get('title', '')
        variant = self.request.GET.get('variant', '')
        print(variant)
        price_from = self.request.GET.get('price_from', '')
        price_to = self.request.GET.get('price_to', '')
        date = self.request.GET.get('date', '')
        

        if title:
            object_list = object_list.filter(title__icontains=title)
        if variant:
            object_list = object_list.filter(productvariant__variant_title__exact=variant)
        if price_from:
            object_list = object_list.filter(productvariantprice__price__gte=price_from)
        if price_to:
            object_list = object_list.filter(productvariantprice__price__lte=price_to)
        if date:
            object_list = object_list.filter(created_at__gte=date)
      

        return object_list

    def get_context_data(self, **kwargs):
        context = super(ListProductView, self).get_context_data(**kwargs)

      

        context['product'] = True
        context['variant_prices'] = ProductVariantPrice.objects.all()
        context['variants'] = Variant.objects.prefetch_related('productvariant_set').distinct()

        context['product_variants'] = ProductVariant.objects.values('variant__title', 'variant_title').distinct().order_by('variant__title')

        return context


