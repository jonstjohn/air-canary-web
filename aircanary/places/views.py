from django.shortcuts import render

from django.views.generic import TemplateView

class HomeView(TemplateView):
    """
    Home page view
    """
    template_name = 'places/home.html'

    def get_context_data(self, **kwargs):

        context = super(HomeView, self).get_context_data(**kwargs)
        lat = float(self.request.GET.get('lat', 40.7500))
        lon = float(self.request.GET.get('lon', -111.8833))

        from places.models import Place
        p = Place(lat, lon)
        context['place'] = p

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
