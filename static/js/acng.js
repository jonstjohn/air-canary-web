var app = angular.module('acApp', []).config( function($routeProvider, $locationProvider, $interpolateProvider) {
    $routeProvider.when('/', {
        templateUrl: '/ng/home',
        controller: HomeCntl
    });

    $routeProvider.when('/site/:code', {
        templateUrl: '/ng/site',
        controller: SiteCntl
    });

    $routeProvider.when('/api', {
        templateUrl: '/ng/api',
        controller: ApiCntl
    });

    $routeProvider.when('/about', {
        templateUrl: '/ng/about',
        controller: AboutCntl
    });

    $routeProvider.when('/contact', {
        templateUrl: '/ng/contact',
        controller: ContactCntl
    });

    $interpolateProvider.startSymbol('{[{');
    $interpolateProvider.endSymbol('}]}');

});

angular.module("acApp").factory("siteService", function(){

  return {sharedObject: {data: null } }
});

function MainCntl($scope, $http, siteService) {

    $scope.sites = siteService.sharedObject.data;

    $scope.loadSites = function() {

        var httpRequest = $http({
            method: 'GET',
            url: '/api/site'
        }).success(function(data, status) {
            $scope.sites = data;
            siteService.sharedObject.data = data;
        });
    };

    $scope.loadSites();

    
}

function HomeCntl($scope, $route, $routeParams, $location, siteService) {
    $scope.$route = $route;
    $scope.$location = $location;
    $scope.$routeParams = $routeParams;
}

function SiteCntl($scope, $route, $routeParams, $http, $location, siteService) {

    $scope.$route = $route;
    $scope.$location = $location;
    $scope.$routeParams = $routeParams;

    $scope.data = [];
    $scope.sites = siteService.sharedObject.data;
    $scope.forecast = [];

    $scope.code = $routeParams.code;

    $scope.init = function(code) {

        console.log($location);
        $scope.code = code;
        $scope.loadData();
        $scope.loadSites();
    }

    $scope.$watch('code', function() { $scope.setSiteName(); $scope.loadData(); });

    $scope.loadData = function() {
        $scope.data = [];
        $location.path('/site/' + $scope.code);
        var httpRequest = $http({
            method: 'GET',
            url: '/api/site/' + $scope.code + '/10'
        }).success(function(data, status) {
            $scope.data = data.data;
            $scope.forecast = data.forecast;
        });
    };

    $scope.setSiteName = function() {
        for (var i = 0; i < $scope.sites.length; i++) {
            if ($scope.sites[i].code == $scope.code) {
                $scope.name = $scope.sites[i].name;
            }
        }
    };

    $scope.loadData();

}

function ApiCntl($scope) {


}

function AboutCntl($scope) {


}
function ContactCntl($scope) {


}

app.directive('sampleGraph', function() {

    // constants
    var margin = 20,
        width = 960,
        height = 500 - .5 - margin,
        color = d3.interpolateRgb("#f77", "#77f");

    return {
        restrict: 'E',
        scope: {
            val: '='
        },
        link: function (scope, element, attrs) {

            // set up initial svg object
            var vis = d3.select(element[0])
                .append("svg")
                .attr("width", width)
                .attr("height", height + margin + 100);


            scope.$watch('exp', function(newVal, oldVal) {

            });
        }
    };

});
