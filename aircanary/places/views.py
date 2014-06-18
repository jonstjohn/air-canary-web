from django.shortcuts import render

from django.views.generic import TemplateView

class HomeView(TemplateView):
    """
    Home page view
    """
    template_name = 'places/home.html'

    def get_context_data(self, **kwargs):

        context = super(HomeView, self).get_context_data(**kwargs)

        if 'lat' in self.kwargs and 'lon' in self.kwargs:
            lat = float(self.kwargs['lat']) # SLC: 40.7500
            lon = float(self.kwargs['lon']) # SLC: -111.8833
        else:
            lat = 40.7500
            lon = -111.8833

        from airnow.grib import AirNowGrib
        a = AirNowGrib()
        r = a.data_latlon(lat, lon)
        if 'ozone' in r:
            context['combined'] = r['ozone'] if float(r['ozone']) > float(r['pm25']) else r['pm25']

        context['pm25'] = r['pm25']
        context['ozone'] = r['ozone']
        context['today'] = r['today']
        context['tomorrow'] = r['tomorrow']

        return context

    """
    def point(latlon):
        from grib import AirNowGrib

        lat, lon = latlon.split(',')

        a = AirNowGrib()
        response_data = a.data_latlon(float(lat), float(lon))
        if 'ozone' in response_data:
            response_data['combined'] = response_data['ozone'] if float(response_data['ozone']) > float(response_data['pm25']) else response_data['pm25']

        response = Response(json.dumps(response_data), status=200, mimetype='text/html')
        return response
    """
