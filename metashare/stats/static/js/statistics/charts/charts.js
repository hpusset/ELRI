import * as filters from './filters.js';

const API_URLS = {
    "TUChart": "charts/tu/",
    "GroupsDataChart": "charts/groups/",
    "DomainsDataChart": "charts/domains/",
    "CreationDateChart": "charts/creation-date/"
}

class BaseChart {
    constructor() {
        if(typeof google === "undefined") { throw new Error("Google Charts library is not loaded."); }
        this.url = null;
        this.chart = null;
        this.chartType = null;
        this.headers = null;
        this.filters = null;
        this.options = {
            chartArea: {
                left: 0,
                height: "80%",
                width: "100%"
            },
            animation: {
                startup: true,
                duration: 1000,
                easing: "out"
            }
        };
        this.extraOptions = {};
    }

    init(container, urlParams={}) {
        // Initialize chart
        var _this = this;
        this.container = container;
        if(!this.url) { throw new Error("URL is not defined"); };
        if(this.filters && !this.filters instanceof filters.ChartFilters) { throw new Error("Object filters is not instance of `ChartFilters`")};
        this.drawChart(urlParams);
    }

    formatData(data) {
        // Format data to this example format: [["Title", 1], ["Title2", 2]].
        let tmpData = _.map(data, (value, key) => [_.capitalize(key), value]);
        tmpData.splice(0, 0, this.headers);
        return tmpData;
    }

    drawChart(urlParams) {
        // Draw chart object with Google Charts library
        var _this = this;
        if (!this.chartType) { throw new Error("Chart type is not defined")};
        if (!this.headers) { throw new Error("Chart headers are not defined.")};
        $.get(this.url, urlParams).done(data => {
            if(!data.errors) {
                // Get data from `this.url`, splice array with
                // `this.chartHeaders` and draw it.
                var chartData = new google.visualization.arrayToDataTable(_this.formatData(data));
                _this.chart = new this.chartType(this.container);
                _this.chart.draw(chartData, this.chartOptions, this.is3D);
            } else {
                throw new Error(data.errors);
            };
        });

    }

    get chartOptions() {
        return Object.assign(this.options, this.extraOptions);
    }
}

class TUChart extends BaseChart {
    constructor() {
        super();
        this.url = API_URLS.TUChart;
        this.chartType =  google.visualization.ColumnChart;
        this.headers = [gettext("TU"), gettext("Total")];
        this.extraOptions = {
            "title": gettext("Resources per data size"),
        };
    }
}

class GroupsDataChart extends BaseChart {
    constructor() {
        super();
        this.url = API_URLS.GroupsDataChart;
        this.chartType = google.visualization.ColumnChart;
        this.headers = [gettext("Group"), gettext("Resources number")];
        this.extraOptions = {
            "title": gettext("Data per groups")
        };
    }
}

class DomainsDataChart extends BaseChart {
    constructor() {
        super();
        this.url = API_URLS.DomainsDataChart;
        this.chartType = google.visualization.PieChart;
        this.headers = [gettext("Domains"), gettext("Total")];
        this.options = {
            "title": gettext("Data per domains")
        };
        this.extraOptions = {
            is3D: true
        }
    }
}

class CreationDateChart extends BaseChart {
    constructor() {
        super();
        this.url = API_URLS.CreationDateChart;
        this.chartType = google.visualization.LineChart;
        this.headers = [gettext("Date"), gettext("Resources")];
        this.filters = new filters.DateFilters();
        this.extraOptions = {
            "title": gettext("Data per dates"),
        };
    }
}


export {
    BaseChart,
    TUChart,
    GroupsDataChart,
    DomainsDataChart,
    CreationDateChart
};
