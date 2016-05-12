var API_HOST = "http://192.168.42.1/";

angular.module('starter.services', [])

.factory('SpiderService', function($http) {
  

  // Some fake testing data
  var spiderData = [];

  return {
    getFromSpider: function() {
		return $http.get(API_HOST+"app").then(function(response){
				console.log(response);
				return response;
			});
      return spiderData;
    }
  };
})

.factory('ServoDataService', function($http) {
  // Some fake testing data
  var spiderData = [];

  return {
    get: function(callback) {
		return $http.get(API_HOST+"app/servodata").then(function(response){
				callback(response.data);
			});
      return spiderData;
    }
  };
});
