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

angular.module("acApp").factory('dataService', function() {

    return { sharedObject: { data: null } };

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

function SiteCntl($scope, $route, $routeParams, $http, $location, siteService, dataService) {

    $scope.$route = $route;
    $scope.$location = $location;
    $scope.$routeParams = $routeParams;

    $scope.data = dataService.sharedObject.data;
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
        siteService.sharedObject.data = [];
        $location.path('/site/' + $scope.code);
        var httpRequest = $http({
            method: 'GET',
            url: '/api/site/' + $scope.code + '/10'
        }).success(function(data, status) {
            dataService.sharedObject.data = data.data;
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

app.directive('sampleGraph', function(dataService) {

    // constants
    var margin = 20,
        width = 960,
        height = 500 - .5 - margin,
        color = d3.interpolateRgb("#f77", "#77f");

    // create a simple data array that we'll plot with a line (this array represents only the Y values, X will just be the index location)
    var data = [3, 6, 2, 7, 5, 2, 0, 3, 8, 9, 2, 5, 9, 3, 6, 3, 6, 2, 7, 5, 2, 1, 3, 8, 9, 2, 5, 9, 2, 7];

    // X scale will fit all values from data[] within pixels 0-w
    var x = d3.scale.linear().domain([0, data.length]).range([0, width]);
    // Y scale will fit values from 0-10 within pixels h-0 (Note the inverted domain for the y-scale: bigger is up!)
    var y = d3.scale.linear().domain([0, 10]).range([height, 0]);
        // automatically determining max range can work something like this
        // var y = d3.scale.linear().domain([0, d3.max(data)]).range([h, 0]);

    return {
        restrict: 'E',
        scope: {
            val: '='
        },
        link: function (scope, element, attrs) {

            // set up initial svg object
            var vis = d3.select(element[0])
                .append("svg")
                .attr('class', 'chart')
                .attr("width", width)
                .attr("height", height + margin + 100);
            // A label for the current year.
            var title = vis.append("text")
                .attr("class", "title")
                .attr("dy", ".71em")
                .text(2000);

            vis.selectAll("rect").data(data).enter().append('rect')
                .attr('y', function(d, i) { return i * 20 })
                .attr('width', x)
                .attr('height', 20);

            scope.$watch('exp', function(newVal, oldVal) {

            });
        }
    };

});
