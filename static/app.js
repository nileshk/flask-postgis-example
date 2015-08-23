$(document).ready(function () {
	var latitude = -81.7170;
	var longitude = 27.8333;


	var map = new ol.Map({
		target: 'map',
		layers: [
			new ol.layer.Tile({
				source: new ol.source.OSM()
			})
		],
		view: new ol.View({
			center: ol.proj.transform([latitude, longitude], 'EPSG:4326', 'EPSG:3857'),
			zoom: 5
			// maxZoom: 17
		})
	});
	var view = map.getView();

	var geoJSONFormat = new ol.format.GeoJSON({
		'defaultDataProjection': 'EPSG:4326' // view.getProjection()
	});

	var source = new ol.source.GeoJSON({
		projection: view.getProjection()
	});

	var image = new ol.style.Circle({
		radius: 7,
		fill: null,
		stroke: new ol.style.Stroke({color: 'red', width: 5})
	});
	var styles = {
		'Point': [new ol.style.Style({
			image: image
		})]
	};
	var styleFunction = function (feature, resolution) {
		var geometryType = feature.getGeometry().getType();
		return styles[geometryType];
	};

	var layer = new ol.layer.Vector({
		title: 'Points of Interest',
		source: source,
		style: styleFunction
	});

	map.addLayer(layer);

	$.ajax({
		url: pointsOfInterestUrl,
		type: 'GET',
		dataType: 'json',
		contentType: 'application/json',
		mimeType: 'application/json',
		success: function (data) {
			var features = geoJSONFormat.readFeatures(data.result, {featureProjection: view.getProjection()});
			console.log(features);
			source.addFeatures(features);
		},
		error: function (data, status, er) {
			console.log(er);
		}
	});

	var element = document.getElementById('popup');

	var popup = new ol.Overlay({
		element: element,
		positioning: 'bottom-center',
		stopEvent: false
	});
	map.addOverlay(popup);

	// display popup on click
	map.on('click', function (evt) {
		var feature = map.forEachFeatureAtPixel(evt.pixel,
			function (feature, layer) {
				console.log(feature);
				return feature;
			});
		if (feature) {
			var geometry = feature.getGeometry();
			var coord = geometry.getCoordinates();
			popup.setPosition(coord);
			$(element).popover('destroy')
				.popover({
					'placement': 'top',
					'html': true,
					'content': feature.get('name')
				})
				.popover('show');
		} else {
			$(element).popover('destroy');
		}
	});

});
