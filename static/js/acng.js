var app = angular.module('acApp', ['ngRoute']).config( function($routeProvider, $locationProvider, $interpolateProvider) {
    $routeProvider.when('/', {
        templateUrl: '/ng/home',
        controller: HomeCntl
    });

    $routeProvider.when('/site/:code', {
        templateUrl: '/ng/site',
        controller: SiteCntl
    });

    $interpolateProvider.startSymbol('{[{');
    $interpolateProvider.endSymbol('}]}');

});

function HomeCntl($scope, $route, $routeParams, $location) {
    $scope.$route = $route;
    $scope.$location = $location;
    $scope.$routeParams = $routeParams;
}

function SiteCntl($scope, $route, $routeParams, $http, $location) {

    $scope.$route = $route;
    $scope.$location = $location;
    $scope.$routeParams = $routeParams;

    $scope.data = [];
    $scope.sites = [];
    $scope.forecast = [];

    $scope.init = function(code) {

        console.log($location);
        $scope.code = code;
        $scope.loadData();
        $scope.loadSites();
    }

    $scope.$watch('code', function() { $scope.setSiteName(); $scope.loadData(); });

    $scope.loadData = function() {
        $scope.data = [];
        var httpRequest = $http({
            method: 'GET',
            url: '/api/site/' + $scope.code + '/10'
        }).success(function(data, status) {
            $scope.data = data.data;
            $scope.forecast = data.forecast;
        });
    };

    $scope.loadSites = function() {

        var httpRequest = $http({
            method: 'GET',
            url: '/api/site'
        }).success(function(data, status) {
            $scope.sites = data;
            $scope.setSiteName();
        });
    };

    $scope.setSiteName = function() {
        for (var i = 0; i < $scope.sites.length; i++) {
            if ($scope.sites[i].code == $scope.code) {
                $scope.name = $scope.sites[i].name;
            }
        }
    };

}
