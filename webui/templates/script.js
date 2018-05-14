// pull data
Highcharts.setOptions({
    global: {
        useUTC: false
    }
});

// Create the chart
Highcharts.stockChart('outputDiv', {
    chart: {
        events: {
            load: function () {
                var series = this.series[0];
                setInterval(function () {
					var req = new XMLHttpRequest();
					req.open("GET", "results", true);
					req.onload = function () {
						if (req.status == 200) {
							var jsonData = JSON.parse(req.responseText);
							var str = JSON.stringify(jsonData, null, 2);
							console.log(str);
							var data = jsonData['predict_results'];
							for(i in data) {
								predict = data[i]
								var str = JSON.stringify(predict, null, 2);
								console.log(str);
								var x = (new Date()).getTime() + predict['timestamp'], // current time
								y = predict['proba'];
								if(y !== undefined)
									series.addPoint([x, y], true, true);
							}
						}
					};
					req.send();
                }, 1000);
            }
        }
    },

    rangeSelector: {
        buttons: [{
            count: 1,
            type: 'minute',
            text: '1M'
        }, {
            count: 5,
            type: 'minute',
            text: '5M'
        }, {
            type: 'all',
            text: 'All'
        }],
        inputEnabled: false,
        selected: 0
    },

    title: {
        text: 'Live random data'
    },

    exporting: {
        enabled: false
    },

    series: [{
        name: 'Predict results',
        data: (function () {
            var data = [],
                time = (new Date()).getTime(),
                i;

			 for (i = -999; i <= 0; i += 1) {
                data.push([
                    time + i * 1000,
                    0.0
                ]);
            }
            return data;
        }())
    }]
});






