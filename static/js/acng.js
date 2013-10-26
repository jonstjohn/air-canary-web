var app = angular.module('acApp', []).config( function($routeProvider, $locationProvider, $interpolateProvider, $httpProvider) {
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

app.filter('dir', function() {
    return function(degrees) {
        var directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
            'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];

        var i = parseInt((degrees + 11.25) / 22.5);
        return directions[i % 16];
    }
});

app.filter('boxName', function() {
    return function(name) {
        return name.substring(0, 3);
    }
});

app.filter('forecastColor', function() {
    return function(description) {
        if (description == 'Good') {
            return 'green';
        } else if (description == 'Moderate') {
            return 'yellow';
        } else if (description == 'Unhealthy for Sensitive Groups') {
            return 'orange';
        } else if (description == 'Unhealthy') {
            return 'red';
        } else {
            return 'unknown';
        }
    };
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

function MainCntl($scope, $http, siteService, $location) {

    var success_callback = function(p) {
        var latitude = p.coords.latitude;
        var longitude = p.coords.longitude;
        console.log(latitude);
        console.log(longitude)
        var url = '/location/' + latitude + '/' + longitude;
        console.log(url);
        $http.get(url)
            .success(function(data, status) {
                console.log($location.path());
                if ($location.path() === '/') {
                    $location.path('/site/' + data.code);
                }
            });
    };

    var error_callback = function(p) {
        console.log('failed location');
        console.log(p);
        $location.path('/site/slc');
    };

    if (geoPosition.init()){  // Geolocation Initialisation
        console.log("Checking geoposition");
        geoPosition.getCurrentPosition(success_callback,error_callback,{enableHighAccuracy:true});
    } else {
        console.log("Geoposition not available");
        $location.path('/site/slc');
        // You cannot use Geolocation in this device
    }

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

function HomeCntl($scope, $route, $routeParams, $http, $location, siteService, dataService) {
    $scope.$route = $route;
    $scope.$location = $location;
    $scope.$routeParams = $routeParams;

    dataService.sharedObject.data = [];
    var httpRequest = $http({
        method: 'GET',
        url: '/api/site/slc/12'
    }).success(function(data, status) {
        dataService.sharedObject.data = data.data;
        $scope.data = data.data;
        $scope.forecast = data.forecast;
    });


}

function SiteCntl($scope, $route, $routeParams, $http, $location, siteService, dataService) {

    $scope.$route = $route;
    $scope.$location = $location;
    $scope.$routeParams = $routeParams;

    $scope.data = dataService.sharedObject.data;
    $scope.sites = siteService.sharedObject.data;
    $scope.forecast = [];

    $scope.code = $routeParams.code;
    
    /*
    var setReload = function() {
        // Refresh every 5 minutes
        $scope.timeout = setInterval(function() {
            $scope.loadData();
        }, 10000); // 300000);
    };
    */
    $scope.$watch('code', function() {
        $scope.setSiteName();
        $scope.loadData(); 
    /*
        if ($scope.timeout) {
            console.log('clear interval');
            window.clearInterval($scope.timeout);
        }
        setReload();
    */
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
/*
    // Refresh every 5 minutes
    timeout = setInterval(function() {
        $scope.loadData(); 
    }, 10000); // 300000);
*/
    $scope.setSiteName = function() {
        if ($scope.sites === null) {
            return "";
        }

        for (var i = 0; i < $scope.sites.length; i++) {
            if ($scope.sites[i].code == $scope.code) {
                $scope.name = $scope.sites[i].name;
            }
        }
    };

    $scope.loadSite = function(code) {
        $location.path('/site/' + code);
    };

    //$scope.loadData();

}

function ApiCntl($scope) {


}

function AboutCntl($scope) {


}
function ContactCntl($scope, $http, $timeout) {

    $scope.send = function(contact) {
        $http.post('/contact', {'contact': contact })
            .success( function() {
                contact.success = true;
                contact.comment = "";
                $timeout(function() { contact.success = false; }, 5000);
            });
    }
}

app.directive('sampleGraph', function(dataService) {

    // constants
    var margin = {top: 20, right: 10, bottom: 40, left: 10},
        width = 960,
        height = 300,
        barPadding = 1,
        color = d3.interpolateRgb("#f77", "#77f");

    var ranges = {
        'pm25': [
            {label: 'Good (<12)', max: 12.0, color: '#5E8C6F', width: 20, x: 0, class: 'bar-green'},
            {label: 'Moderate (12.1-35.4)', max: 35.4, color: '#F0C866', width: 70, x: 130, class: 'bar-yellow'},
            {label: 'Unhealthy for Sensitive People (35.5-55.4)', max: 55.4, color: '#DC9C5E', width: 150, x: 310, class: 'bar-orange'},
            {label: 'Unhealthy (>55.5)', max: 1000.0, color: '#DC4358', width: 100, x: 620, class: 'bar-red'}
        ],
        'ozone': [
            {label: 'Good (<0.059)', max: 0.059, color: '#5E8C6F', width: 20, x: 0, class: 'bar-green'},
            {label: 'Moderate (0.06-0.075)', max: 0.075, color: '#F0C866', width: 70, x: 150, class: 'bar-yellow'},
            {label: 'Unhealthy for Sensitive People (0.076-0.095)', max: 0.095, color: '#DC9C5E', width: 150, x: 350, class: 'bar-orange'},
            {label: 'Unhealthy (>0.096)', max: 1000.0, color: '#DC4358', width: 100, x: 680, class: 'bar-red'}
        ],
        'nox': [
            {label: 'Good (<0.059)', max: 0.059, color: '#5E8C6F', width: 20, x: 0, class: 'bar-green'},
            {label: 'Moderate (0.06-0.075)', max: 0.075, color: '#F0C866', width: 70, x: 150, class: 'bar-yellow'},
            {label: 'Unhealthy for Sensitive People (0.076-0.095)', max: 0.095, color: '#DC9C5E', width: 150, x: 350, class: 'bar-orange'},
            {label: 'Unhealthy (>0.096)', max: 1000.0, color: '#DC4358', width: 100, x: 680, class: 'bar-red'}
        ],

    };


    return {
        restrict: 'E',
        scope: {
            val: '='
        },
        link: function (scope, element, attrs) {

            if (attrs.width) {
                var width = parseInt(attrs.width, 10);
            }

            if (attrs.height) {
                var height = parseInt(attrs.height, 10);
            }

            // set up initial svg object
            var vis = d3.select(element[0])
                .append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append('g')
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            // Create legend
            if (attrs.nolegend !== '1') {
                var legendSvg = d3.select(element[0])
                    .append("svg")
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", 25)
                    .append('g')
                    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
            }

            // Watch for data changes
            scope.$watch('val', function(newVal, oldVal) {

                vis.selectAll('*').remove();

                // Clear existing graph
                if (!newVal) {
                    return;
                }

                var data = [];
                for (var i = 0; i < newVal.length; i++) {
                    var val = newVal[i][attrs.type] ? newVal[i][attrs.type] : 0;

                    // For now, just format everything in mountain time
                    data.push([val, moment(newVal[i].observed).tz("America/Denver").format()]);
                }

                var range = ranges[attrs.type];

                var yMax = d3.max(data, function(d) { return d[0]; });
                var yTicks = [];
                for (var i = 0; i < range.length; i++) {
                    yTicks.push(range[i]);
                    if (range[i].max >= yMax) {
//                        yTicks.push(range[i]);
                        yMax = range[i].max;
                        break;
                    }
                }

                var yScale = d3.scale.linear().domain([0, yMax]).range([0, height]);
                var xScale = d3.scale.linear().domain([0, 24]).range([0, width]);

                var yAxis = d3.svg.axis().scale(yScale).tickSize(width).orient('right');

                var barColor = function(val) {
                    if (val == 0) {
                        return 'bar-none';
                    }
                    for (var i = 0; i < ranges[attrs.type].length; i++) {
                        if (parseFloat(val) <= ranges[attrs.type][i].max) {
                            return ranges[attrs.type][i].class;
                        }
                    }

                    return '';
                };

                // Horizontal threshold lines
                vis.selectAll('line')
                    .data(yTicks)
                    .enter().append('line')
                        .attr('x1', 0)
                        .attr('x2', width)
                        .attr('y1', function(d, i) { return height - yScale(d.max); })
                        .attr('y2', function(d, i) { return height - yScale(d.max); })
                        .style('stroke', '#ccc');

                vis.selectAll('.rule')
                        .data(yTicks)
                    .enter().append('text')
                        .attr('class', 'rule')
                        .attr('x', function(d, i) { return 0; })
                        .attr('y', function(d, i) { return height - yScale(d.max); })
                        .attr('dy', '15')
                        .attr('text-anchor', 'right')
                        .style('font-size', '10px')
                        .style('fill', '#999')
                        .text(function(d, i) { return d.label; });
               
                // Bars
                vis.selectAll("rect")
                        .data(data)
                    .enter().append('rect')
                        .attr('x', function(d, i) { return i * (width / data.length); })
                        .attr('width', function(d, i) { return width / data.length - barPadding; })
                        .attr('height', function(d, i) { return d[0] == 0 ? 30 : yScale(d[0]); })
                        .attr('y', function(d, i) { return height - (d[0] == 0 ? 30 : yScale(d[0])); })
                        .attr("class", function(d) { return barColor(d[0]); });

                var formatTime = function(dateTime) {
                    var parts = dateTime.split("T");
                    var timeParts = parts[1].split(":");
                    var hour = parseInt(timeParts[0], 10);
                    var min = timeParts[1];
                    var ampm = " AM";

                    if (hour > 12) {
                        hour = hour - 12;
                        ampm = ' PM';
                    }

                    return hour + ":" + min + ampm;
                };

                var formatDate = function(dateTime) {
                    var parts = dateTime.split("T");
                    var dateParts = parts[0].split("-");
                    return dateParts[1] + "/" + dateParts[2];
                }

                // Bar labels
                if (attrs.nolabels !== "1") {

                    vis.selectAll("text.labels")
                        .data(data)
                        .enter()
                        .append("text")
                        .text(function(d) {
                            var label = d[0] == 0 ? 'n/a' : d[0];
                            return label;
                        })
                        .attr("x", function(d, i) {
                            return i * (width / data.length) + (width / data.length - barPadding) / 2;
                        })
                        .attr("y", function(d) {
                            return height - (d[0] == 0 ? 30 : yScale(d[0])) + 14;
                        })
                        .attr('font-family', 'sans-serif')
                        .attr('font-size', '11px')
                        .attr('fill', 'white')
                        .attr('text-anchor', 'middle');

                }

                vis.selectAll("text.yaxis")
                    .data(data)
                    .enter()
                    .append("text")
                    .text(function(d, i) {
                        var label = i == data.length - 1 || i % 4 == 0 ? formatTime(d[1]) : ""; 
                        return label;
                    })
                    .attr("x", function(d, i) {
                        return i * (width / data.length) + (width / data.length - barPadding) / 2;
                    })
                    .attr("y", function(d) {
                        return height + 15;
//                        return height - yScale(d) + 14;
                    })
                    .attr('font-family', 'sans-serif')
                    .attr('font-size', '10px')
                    .attr('fill', 'black')
                    .attr('text-anchor', 'middle');

                vis.selectAll("text.yaxis")
                    .data(data)
                    .enter()
                    .append("text")
                    .text(function(d, i) { return i == data.length - 1 || i % 4 == 0 ? formatDate(d[1]) : ""; })
                    .attr("x", function(d, i) {
                        return i * (width / data.length) + (width / data.length - barPadding) / 2;
                    })
                    .attr("y", function(d) {
                        return height + 30;
//                        return height - yScale(d) + 14;
                    })
                    .attr('font-family', 'sans-serif')
                    .attr('font-size', '10px')
                    .attr('fill', 'black')
                    .attr('text-anchor', 'middle');

                if (attrs.nolegend !== "1") {

                    var legend = legendSvg.append('g')
                        .attr('class', 'legend')
                        .attr('height', 100)
                        .attr('widgth', 100)
                        .attr('tranform', 'translate(-20, 50)');

                    legend.selectAll('rect')
                        .data(ranges[attrs.type])
                        .enter()
                        .append('rect')
                        .attr('x', function(d, i) { return d.x; }) //return i * 270; })
                        .attr('y', -10)
                        .attr('width', 10)
                        .attr('height', 10)
                        .attr('class', function(d) { return d.class; });

                    legend.selectAll('text')
                        .data(ranges[attrs.type])
                        .enter()
                        .append('text')
                        .attr('x', function(d, i) { return d.x + 20; })
                        .attr('y', 0)
                        .text(function(d) {
                            return d.label; 
                        });

                }
/*
                var gy = vis.append('g').call(yAxis);

                gy.selectAll("g").filter(function(d) { return d; })
                    .classed("minor", true);

                gy.selectAll("text")
                    .attr("x", 4)
                    .attr("dy", -4);
*/

            });

        }
    };

});
