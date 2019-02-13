import * as charts from './charts/charts.js';
import * as filters from './charts/filters.js';

// Default loaded chart
const DEFAULT_CHART = "translation-units";

// Chart mapping with types of select input
const CHART_TYPE_MAPPING = {
    'translation-units': charts.TUChart,
    'group-data': charts.GroupsDataChart,
    'domains-data': charts.DomainsDataChart,
    'creation-date-data': charts.CreationDateChart,
}


class StatisticsView {
    constructor() {
        this.container = document.getElementsByClassName('content_tab')[0];
        this.statisticsChoiceForm = document.getElementById("statistics-form");
        this.chartFiltersContainer = document.getElementById("chart-filters");
        this.chartContainer = document.getElementById("chart-container");
        this.statisticsChoiceForm.querySelector("#statistics-choice").addEventListener("change", this.selectChanged.bind(this));
        this.currentChart = null;
        document.addEventListener("googleLoaded", this.init.bind(this));

    }

    init() {
         // Get default `chartObj` and load this one.
        var chartObj = this.getChartObj(DEFAULT_CHART);
        this.loadChart(chartObj);
    }

    getChartType() {
        var select = this.statisticsChoiceForm.querySelector("#statistics-choice");
        return select.value;
    }

    getChartObj(chartType) {
        // Return selected `chartObj` with `chartType` or null if this
        // one is not defined.
        try {
            var chartObj = CHART_TYPE_MAPPING[chartType];
        } catch(e) {
            return null;
        };
        return chartObj;
    }

    filtersHandler(event) {
        event.preventDefault();
        this.currentChart.filters.processEvent(event);
        if(this.currentChart.filters.isValid) {
            this.currentChart.drawChart(this.currentChart.filters.urlParams);
        } else {
            alert(this.currentChart.filters.errorMessage);
        }
    }

    loadChart(chartObj, urlParams) {
        // Load `chartObj` in DOM.
        if(chartObj) {
            var _this = this;
            this.currentChart = new chartObj();
            if(this.currentChart.filters) {
                this.currentChart.filters.init(this.chartFiltersContainer);
                this.chartFiltersContainer.addEventListener("submit", this.filtersHandler.bind(this));
                this.chartFiltersContainer.addEventListener(filters.RESET_EVENT, function() {
                    _this.reloadChart(chartObj, {})
                });
            };
            this.currentChart.init(this.chartContainer, urlParams);
        };
    }

    reloadChart(chartObj, urlParams) {
        // Remove chart from the DOM and set it to null if one chart is
        // already loaded before loading new.
        if(this.currentChart) {
            this.currentChart = null;
            this.chartContainer.innerHTML = null;
            this.chartFiltersContainer.innerHTML = null;
        }
        this.loadChart(chartObj, urlParams);
    }

    selectChanged(event) {
        // Get `chartObj` from form select input event value and call to
        // `this.reloadChart` function.
         var target = event.target,
            chartObj = this.getChartObj(target.value);
        this.reloadChart(chartObj);
     }
};

new StatisticsView();
