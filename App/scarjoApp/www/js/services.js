var API_HOST = "http://192.168.42.1/";

angular.module('starter.services', [])

.factory('SpiderService', function($http, $ionicPopup) {
  

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

.factory('ServoDataService', function($http, $ionicPopup) {
  var systemData = [];

  return {
    get: function(callback) {
		return $http.get(API_HOST+"app/servodata").success(function(response){
				callback(response.data);
			})
			.error(function(data, status, headers, config) {
				var confirmPopup = $ionicPopup.confirm({
				 title: 'Oh no!',
				 template: "I can't find Scarjo. Are you sure you are connected to Scarjo-AP "
			   });
			})
			
			;
      return systemData;
    }
  };
})
.factory('SystemDataService', function($http, $ionicPopup) {
  // Some fake testing data
  var spiderData = [];

  return {
    get: function(callback) {
		return $http.get(API_HOST+"app/getsystemdata").success(function(response){
				callback(response.data);
			})
			.error(function(data, status, headers, config) {
				var confirmPopup = $ionicPopup.confirm({
				 title: 'Oh no!',
				 template: "I can't find Scarjo. Are you sure you are connected to Scarjo-AP"
			   });
			})
			;
      return spiderData;
    }
  };
});
