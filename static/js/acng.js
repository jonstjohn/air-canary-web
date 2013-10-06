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

    return {
        sharedObject: {
            data: null,
            echo: function() { console.log('echo'); }
        }
    }
});

angular.module("acApp").factory('dataService', function() {

    return { 
        sharedObject: {
            data: null,
            echo: function() { console.log('echo'); }
        }
    };

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

    $scope.$watch('code', function() {
        $scope.setSiteName();
        $scope.loadData(); 
    });

    $scope.loadData = function() {
        dataService.sharedObject.data = [];
        $location.path('/site/' + $scope.code);
        var httpRequest = $http({
            method: 'GET',
            url: '/api/site/' + $scope.code + '/24'
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

    //$scope.loadData();

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
        height = 300,
        barPadding = 1,
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
            // A label for the current year.
            var title = vis.append("text")
                .attr("class", "title")
                .attr("dy", ".71em")
                .text(2000);

            scope.$watch('val', function(newVal, oldVal) {

                vis.selectAll('*').remove();

                if (!newVal) {
                    return;
                }

                var data = [];
                for (var i = 0; i < newVal.length; i++) {
                    var val = newVal[i].pm25 ? newVal[i].pm25 : 0;
                    data.push(val);
                }

                data.reverse();

                var scale = d3.scale.linear().domain([0, d3.max(data)]).range([0, height]);

                vis.selectAll("rect").data(data).enter().append('rect')
                    .attr('x', function(d, i) { return i * (width / data.length); })
                    .attr('width', function(d, i) { return width / data.length - barPadding; })
                    .attr('height', function(d, i) { return scale(d); })
                    .attr('y', function(d, i) { return height - scale(d); })
                    .attr("fill", function(d) {
                        if (d > 12.0 && d < 35.5) {
                            return "rgb(255, 255, 0)"; // yellow
                        } else if (d >= 35.5 && d <= 55.4) {
                            return "rgb(255, 128, 0)"; // orange
                        } else if (d > 55.4) {
                            return "rgb(0, 0, 204)"; // red
                        } else if (d >= 6.0) {
                            return "rgb(138, 185, 11)"; // light green
                        } else {
                            return "rgb(66, 134, 49)"; // green
                        }
                    });

                // Green 66,134,49
                // Light green 138, 185, 11
                // Yellow 255, 211, 88
                // Orange 255, 159, 38
                // Light red 255, 49, 0
                // Red 254, 0, 0

                vis.selectAll("text")
                    .data(data)
                    .enter()
                    .append("text")
                    .text(function(d) { return d; })
                    .attr("x", function(d, i) {
                        return i * (width / data.length) + (width / data.length - barPadding) / 2;
                    })
                    .attr("y", function(d) {
                        return height - scale(d) + 14;
                    })
                    .attr('font-family', 'sans-serif')
                    .attr('font-size', '11px')
                    .attr('fill', 'white')
                    .attr('text-anchor', 'middle')

            });

        }
    };

});
