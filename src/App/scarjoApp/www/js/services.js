angular.module('starter.services', [])

.factory('SpiderService', function($http) {
  var API_HOST = "http://192.168.42.1/";

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
});
