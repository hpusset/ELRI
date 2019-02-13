const RESET_ID = "reset";
const RESET_EVENT = "reset";

class ChartFilters {
    constructor(templateFilters) {
        this.templateFilters = templateFilters;
        this.errorMessage = null;
    }

    init(container) {
        container.innerHTML += this.html;
        var reset = document.getElementById(RESET_ID);
        if(reset) {
            reset.addEventListener("click", function() {
                var evt = new Event(RESET_EVENT)
                container.dispatchEvent(evt);
            });
        };
    }

    processEvent(event) {
        this.filtersData = new FormData(event.target),
        this.urlParams = Object.fromEntries(this.filtersData.entries())
    }

    get html() {
        return this.templateFilters.innerHTML;
    }

    get isValid() {
        throw new Error("Not implemented");
    }
};


class DateFilters extends ChartFilters {
    constructor(container) {
        super(document.getElementById("tpl-date-filters"), container);
        this.errorMessage = gettext("Invalid filters, end date is lower than start date.")
        $.datepicker.setDefaults({
             "changeMonth": true,
             "changeYear": true,
             "defaultDate": new Date(),
             "dateFormat": "dd-mm-yy"
        });
    }

    init(container) {
        super.init(container);
        $(container).find("#date-picker-start").datepicker();
        $(container).find("#date-picker-end").datepicker();
    }

    get isValid() {
        var startDate = this.stringToDate(this.filtersData.get("start-date")),
            endDate = this.stringToDate(this.filtersData.get("end-date"));
        if(startDate < endDate) {
            return true;
        }
        return false;
    }

    stringToDate(date) {
        return new Date(this.toIsoFormat(date));
    }

    toIsoFormat(date) {
        if(typeof date === "string") {
            let sDate = date.split("-");
            return _.join(_.reverse(sDate), "-");
        }
    }
}

export { ChartFilters, DateFilters, RESET_EVENT };
