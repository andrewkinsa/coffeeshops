# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.http import Http404
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views import View
from geopy.geocoders import Nominatim
import csv
import geopy.distance
import json

geocoder = Nominatim(user_agent='test script')



class Http400(Exception):
    pass


def geocode(address):
    location = geocoder.geocode(address)
    if not location:
        raise Http400('could not geocode "%s"' % address)
    return (location.latitude, location.longitude)



class Shop(object):
    def __init__(self, id, name, address, lat=None, lng=None):
        self.id = int(id)
        self.name = name.strip()
        self.address = address.strip()
        if lat and lng:
            self.coords = (float(lat), float(lng))
        else:
            self.coords = geocode(address)

    def to_dict(self):
        return {'id': self.id,
                'name': self.name,
                'address': self.address,
                'lat': self.coords[0],
                'lng': self.coords[1]}

    def to_json(self):
        return json.dumps(self.to_dict())


class ShopStore(object):
    def __init__(self, filename):
        self.dict = {}
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile, ['id', 'name', 'address', 'lat', 'lng'])
            for row in reader:
                self.add(row)

    def __getitem__(self, shop_id):
        return self.dict[shop_id]

    def exists(self, shop_id):
        return shop_id in self.dict

    def add(self, shop_dict):
        if 'id' in shop_dict:
            shop_id = int(shop_dict['id'])
        elif not self.dict:
            shop_id = 1
        else:
            shop_id = max(self.dict.iterkeys()) + 1
            #TODO: make O(1)
            #TODO: make atomic

        shop_dict['id'] = shop_id
        shop = Shop(**shop_dict)
        self.dict[shop_id] = shop
        return shop

    def delete(self, shop_id):
        del self.dict[shop_id]

    def to_json(self, shop=None):
        if shop:
            return json.dumps([shop.to_dict()])
        else:
            return json.dumps([shop.to_dict() for shop in self.dict.itervalues()])

    def nearest(self, coords):
        return min(self.dict.values(),
                   key=lambda shop: geopy.distance.great_circle(coords, shop.coords))


shops = ShopStore('locations.csv')


class ApiView(View):
    def check_id(self, shop_id):
        if not shops.exists(shop_id):
            raise Http404()

    def get_json(self, request):
        try:
            body = json.loads(request.body)
        except ValueError:
            raise Http400('malformed json')
        if not isinstance(body, dict):
            raise Http400('malformed json')
        for field in ('name', 'address'):
            if field not in body.iterkeys():
                raise Http400('expected ' + field)
        for field in body.iterkeys():
            if field not in ('name', 'address', 'lat', 'lng'):
                raise Http400('unknown field ' + field)
        return body


class ShopListView(ApiView):
    def get(self, request):
        try:
            nearest = None
            nearest_to = request.GET.get('nearest_to')
            if nearest_to:
                coords = geocode(nearest_to)
                nearest = shops.nearest(coords)
            return HttpResponse(shops.to_json(nearest), 'application/javascript')
        except Http400 as e:
            return HttpResponseBadRequest(e.message)

    def post(self, request):
        try:
            body = self.get_json(request)
            shop = shops.add(body)
            return HttpResponse(shop.to_json(), 'application/javascript', status=201)
        except Http400 as e:
            return HttpResponseBadRequest(e.message)


class ShopView(ApiView):
    def get(self, request, shop_id):
        shop_id = int(shop_id)
        self.check_id(shop_id)
        return HttpResponse(shops[shop_id].to_json(), 'application/javascript')

    def delete(self, request, shop_id):
        shop_id = int(shop_id)
        self.check_id(shop_id)
        shops.delete(shop_id)
        return HttpResponse(status=204)

    def put(self, request, shop_id):
        try:
            shop_id = int(shop_id)
            exists = shops.exists(shop_id)
            body = self.get_json(request)
            body['id'] = shop_id
            shop = shops.add(body)
            return HttpResponse(shop.to_json(), 'application/javascript', status=(200 if exists else 201))
        except Http400 as e:
            return HttpResponseBadRequest(e.message)
