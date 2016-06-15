angular.module('starter.controllers', [])

.controller('SpiderCtrl', function($scope, SpiderService, ServoDataService,  $interval) {
	$scope.shouldUpdate = {}
	
	
	$scope.testConnection = function()
	{
		ServoDataService.get(function (data) {
			$scope.servodata = data;
		});
	}
	
	$scope.updateData = function()
	{
		console.log($scope.shouldUpdate.value);
		if($scope.shouldUpdate.value != undefined && $scope.shouldUpdate.value)
		ServoDataService.get(function (data) {
			$scope.servodata = data;
		});
	}
	
	
	$scope.updateInterval = $interval($scope.updateData, 2000);
	
	
	$scope.servodata = [
	{position: "100", speed: "42", load: "2", voltage: "5", temp: "30"}, //Servo Dummy data
	{position: "100", speed: "42", load: "2", voltage: "5", temp: "30"},					
	{position: "100", speed: "42", load: "2", voltage: "5", temp: "30"},					
	{position: "100", speed: "42", load: "2", voltage: "5", temp: "30"},					
	{position: "100", speed: "42", load: "2", voltage: "5", temp: "30"},					
	{position: "100", speed: "42", load: "2", voltage: "5", temp: "30"},					
	{position: "100", speed: "42", load: "2", voltage: "5", temp: "30"},					
	{position: "100", speed: "42", load: "2", voltage: "5", temp: "30"},					
	{position: "100", speed: "42", load: "2", voltage: "5", temp: "30"},					
	{position: "100", speed: "42", load: "2", voltage: "5", temp: "30"},					
	{position: "100", speed: "42", load: "2", voltage: "5", temp: "30"},					
	{position: "100", speed: "42", load: "2", voltage: "5", temp: "30"},					
	{position: "100", speed: "42", load: "2", voltage: "5", temp: "30"},					
	{position: "100", speed: "42", load: "2", voltage: "5", temp: "30"},					
	{position: "100", speed: "42", load: "2", voltage: "5", temp: "30"},					
	{position: "100", speed: "42", load: "2", voltage: "5", temp: "30"},					
	{position: "100", speed: "42", load: "2", voltage: "5", temp: "30"},					
	{position: "100", speed: "42", load: "2", voltage: "5", temp: "30"},					
	]; 
	
	
	$scope.$on('$ionicView.leave', function(e) {
		$scope.shouldUpdate.value = false;
		
		$interval.cancel($scope.updateInterval);
		
	});
})

.controller('GraphsCtrl', function($scope, SystemDataService, $interval) {
  // With the new view caching in Ionic, Controllers are only called
  // when they are recreated or on app start, instead of every page change.
  // To listen for when this page is active (for example, to refresh data),
  // listen for the $ionicView.enter event:
  //
  //$scope.$on('$ionicView.enter', function(e) {
  //});
	$scope.graphOptions = {
		animation : false,
		
		scales: {
            yAxes: [{
                stacked: true
            }]
        }
	};
	
  
	$scope.rawData = {}
	
	$scope.cpuSeries = ["Core 1", "Core 2", "Core 3", "Core 4"];
	$scope.cpuData   = [[0],[0],[0],[0]];
	$scope.cpuLabels = [0];
	
	$scope.tiltSeries = ["Tilt X", "Tilt Y", "Tilt Z"];
	$scope.tiltData  = [[0],[0],[0]];
	$scope.tiltLabels = [0];
	
	$scope.batterySeries = ["Est. Battery Remaining"];
	$scope.batteryData = [[0]];
	$scope.batteryLabels = [0];
	
	$scope.$on('$ionicView.leave', function(e) {
		$scope.shouldUpdate.value = false;
		
		$interval.cancel(updateInterval);
		
	});
	
	
	$scope.updateData = function()
	{
		SystemDataService.get(function (data) {
			$scope.rawData = data
			
			
			//Push the new cpu usage
			if($scope.cpuData[0].length >= 10)
				$scope.cpuData[0].shift();
			if($scope.cpuData[1].length >= 10)
				$scope.cpuData[1].shift();
			if($scope.cpuData[2].length >= 10)
				$scope.cpuData[2].shift();
			if($scope.cpuData[3].length >= 10)
				$scope.cpuData[3].shift();
			
			$scope.cpuData[0].push(data['cpu']['core1']);
			$scope.cpuData[1].push(data['cpu']['core2']);
			$scope.cpuData[2].push(data['cpu']['core3']);
			$scope.cpuData[3].push(data['cpu']['core4']);
			if($scope.cpuLabels.length >= 10)
				$scope.cpuLabels.shift();
			$scope.cpuLabels.push(data['cpu']['time']);
			
			//Push the new tilt values
			if($scope.tiltData[0].length == 10)
				$scope.tiltData[0].shift();
			if($scope.tiltData[1].length == 10)
				$scope.tiltData[1].shift();
			if($scope.tiltData[2].length == 10)
				$scope.tiltData[2].shift();
			
			$scope.tiltData[0].push(data['tilt']['x']);
			$scope.tiltData[1].push(data['tilt']['y']);
			$scope.tiltData[2].push(data['tilt']['z']);
			
			if($scope.cpuLabels.length >= 10)
				$scope.tiltLabels.shift();
			$scope.tiltLabels.push(data['cpu']['time']);
			
			//battery
			if($scope.batteryData[0].length == 10)
				$scope.batteryData[0].shift();
				$scope.batteryLabels.shift();
			$scope.batteryData[0].push(data['battery']);
			$scope.batteryLabels.push(data['cpu']['time']);
			
		});
	}
	
	updateInterval = $interval($scope.updateData, 1500);
	
})

.controller('DebugCtrl', function($scope, $stateParams, SpiderService, $sceDelegate) {
	$scope.debugvars = [{name:"Test variabel", value: "1337"}];
	$scope.camurl = $sceDelegate.trustAs("resourceUrl","http://192.168.42.1/camera");
	$scope.emptyurl = $sceDelegate.trustAs("resourceUrl","");
	$scope.cameraURL = $scope.emptyurl;
	
	$scope.$on('$ionicView.enter', function(e) {
		//Set iframe src here..
		$scope.cameraURL = $scope.camurl;
		
	});
	
	$scope.$on('$ionicView.leave', function(e) {
		//Set iframe to empty src here..
		$scope.cameraURL = $scope.emptyurl;
	});
	
	
})

.controller('SettingsCtrl', function($scope) {
  $scope.settings = {
    autoRefreshData: true
  };
});
