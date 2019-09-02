// Calendar data
const _daysInMonths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
const _weekdayLabels = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const _monthLabels = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const _today = new Date();
const _todayComps = {
  year: _today.getFullYear(),
  month: _today.getMonth() + 1,
  day: _today.getDate(),
};

/***************************************************/
/************* BASE CALENDAR COMPONENT *************/
/***************************************************/

const calendar = Vue.component('calendar', {
  template: '#calendar',
  data() {
    const firstDayOfWeek = new Date();
    firstDayOfWeek.setDate(
      firstDayOfWeek.getDate() - firstDayOfWeek.getDay());

    return {
      month: _todayComps.month,
      year: _todayComps.year,
      day: _todayComps.day,
      firstDayOfWeek: firstDayOfWeek.getDate(),
      occurrences: null,
      loading: true,
      errored: false,
      how_to_display: 'month',
      calendar_filter: null,
      program_filter: null,
    };
  },
  props: {
    dayKey: { type: String, default: 'label' },
  },
  computed: {
    // Our component exposes month as 1-based, but sometimes we need 0-based
    monthIndex() {
      return this.month - 1;
    },
    isLeapYear() {
            return (this.year % 4 === 0 && this.year % 100 !== 0) || this.year % 400 === 0;
    },
    // Day/month/year components for previous month
    previousMonthComps() {
        if (this.month === 1) return {
        days: _daysInMonths[11],
        month: 12,
        year: this.year - 1,
      }
      return {
        days: (this.month === 3 && this.isLeapYear) ? 29 : _daysInMonths[this.month - 2],
        month: this.month - 1,
        year: this.year,
      };
    },
    // Day/month/year components for next month
    nextMonthComps() {
        if (this.month === 12) return {
        days: _daysInMonths[0],
        month: 1,
        year: this.year + 1,
      };
      return {
        days: (this.month === 2 && this.isLeapYear) ? 29 : _daysInMonths[this.month],
        month: this.month + 1,
        year: this.year,
      };
    },
    // State for calendar header (no dependencies yet...)
    months() {
      return _monthLabels.map((ml, i) => ({
        label: ml,
        label_1: ml.substring(0, 1),
        label_2: ml.substring(0, 2),
        label_3: ml.substring(0, 3),
        number: i + 1,
      }));
    },
    // State for weekday header (no dependencies yet...)
    weekdays() {
      return _weekdayLabels.map((wl, i) => ({
        label: wl,
        label_1: wl.substring(0, 1),
        label_2: wl.substring(0, 2),
        label_3: wl.substring(0, 3),
        number: i + 1,
      }));
    },
    // State for the selected week's days
    selectedWeekDays() {
      const days = [];

      for (let i = this.firstDayOfWeek; i < this.firstDayOfWeek + 7; i++) {
				days.push({
					day: i,
					date: new Date(this.year, this.month - 1, i),
					isToday: (i === _todayComps.day &&
						this.month === _todayComps.month &&
						this.year === _todayComps.year),
				});
      }

      return days;
    },
    // State for calendar header
    header() {
      const month = this.months[this.monthIndex];
      return {
        month: month,
        year: this.year.toString(),
        shortYear: this.year.toString().substring(2, 4),
        label: month.label + ' ' + this.year,
        label_month: month.label,
        label_year: this.year,
      };
    },
    // Returns number for first weekday (1-7), starting from Sunday
    firstWeekdayInMonth() {
      return new Date(this.year, this.monthIndex, 1).getDay() + 1;
    },
    // Returns number of days in the current month
    daysInMonth() {
      // Check for February in a leap year
      if (this.month === 2 && this.isLeapYear) return 29;
      // ...Just a normal month
      return _daysInMonths[this.monthIndex];
    },
    weeks() {
      const weeks = [];
      let previousMonth = true, thisMonth = false, nextMonth = false;
      let day = this.previousMonthComps.days - this.firstWeekdayInMonth + 2;
      let month = this.previousMonthComps.month;
      let year = this.previousMonthComps.year;
      // Cycle through each week of the month, up to 6 total
      for (let w = 1; w <= 6 && !nextMonth; w++) {
        // Cycle through each weekday
        const week = [];
        for (let d = 1; d <= 7; d++) {
            
          // We need to know when to start counting actual month days
          if (previousMonth && d >= this.firstWeekdayInMonth) {
            // Reset day/month/year counters
            day = 1;
            month = this.month;
            year = this.year;
            // ...and flag we're tracking actual month days
            previousMonth = false;
            thisMonth = true;
                    }
          
          // Append day info for the current week
          // Note: this might or might not be an actual month day
          //  We don't know how the UI wants to display various days,
          //  so we'll supply all the data we can
          const dayInfo = {
            label: (day && thisMonth) ? day.toString() : '',
            day,
            weekday: d,
            week: w,
            month,
            year,
            date: new Date(year, month - 1, day),
            beforeMonth: previousMonth,
            afterMonth: nextMonth,
            inMonth: thisMonth,
            isToday: day === _todayComps.day && month === _todayComps.month && year === _todayComps.year,
            isFirstDay: thisMonth && day === 1,
            isLastDay: thisMonth && day === this.daysInMonth,
          };
          this.$emit('configureDay', dayInfo);
          week.push(dayInfo);
          
          // We've hit the last day of the month
          if (thisMonth && day >= this.daysInMonth) {
            thisMonth = false;
            nextMonth = true;
            day = 1;
            month = this.nextMonthComps.month;
            year = this.nextMonthComps.year;
          // Still in the middle of the month (hasn't ended yet)
          } else {
            day++;
          }
        }
        // Append week info for the month
        weeks.push(week);
      }
      return weeks;
    },
  },
  methods: {
    eventIsSameDay(day, month, year, in_time) {
      let start_time = new Date(in_time);
      //console.log(in_time, start_time, day, month, year);
      let in_day = (start_time.getDay() == day && start_time.getMonth() == month && start_time.getYear() == year);
      //console.log(in_day);
      return in_day;
    },
    calMonthSelectDisplay() {
      this.how_to_display = 'month';
      this.loadMonthlyOccurrences();
    },
    calWeekSelectDisplay() {
      this.how_to_display = 'week';
      this.loadWeeklyOccurrences();
    },
    //calYearSelectDisplay() {
    //  this.how_to_display = 'year';
    //},
    moveThisMonth() {
      this.month = _todayComps.month;
      this.year = _todayComps.year;
      this.loadMonthlyOccurrences();
    },
    moveNextMonth() {
      const { month, year } = this.nextMonthComps;
      this.month = month;
      this.year = year;
      this.loadMonthlyOccurrences();
    },
    movePreviousMonth() {
      const { month, year } = this.previousMonthComps;
      this.month = month;
      this.year = year;
      this.loadMonthlyOccurrences();
    },
    moveNextYear() {
      this.year++;
      this.loadMonthlyOccurrences();
    },
    movePreviousYear() {
      this.year--;
      this.loadMonthlyOccurrences();
    },
    loadMonthlyOccurrences() {
      this.loading = true;
      var cur_url = window.location.href
      var cur_host = cur_url.split("/");
      url = cur_host[0] + "//" + cur_host[2] + '/api/atria/calendar/' + this.year + '/' + this.month + '/';
      axios
        .get(url)
        .then(response => {
          this.occurrences = response.data.occurrences
        })
        .catch(error => {
          console.log(error)
          this.errored = true
        })
        .finally(() => this.loading = false)
    },
    loadWeeklyOccurrences() {
      const day = new Date();
      day.setDate(day.getDate() - day.getDay());
      const url = encodeURI('/api/atria/calendar/' +
        `${this.year}/${this.month}/${day.getDate()}/?week=true`);

      axios
        .get(url)
        .then(response => {
          this.occurrences = response.data.occurrences;
        })
        .catch(error => {
          console.log(error);
          this.errored = true;
        })
        .finally(() => {
          this.loading = false;
        });
    }
  },
  mounted () {
    this.loadMonthlyOccurrences();
  },
});

/*************************************************/
/************* DATE PICKER COMPONENT *************/
/*************************************************/

Vue.component('single-date-picker', {
  created() {
    this.$on('configureDay', this.configureDay);
    this.$on('selectDay', this.selectDay);
  },
  extends: calendar,
  props: {
    value: Date,
  },
  computed: {
    hasValue() {
      return this.value && typeof this.value.getTime === 'function';
    },
    valueTime() {
        return this.hasValue ? this.value.getTime() : null;
    },
  },
  methods: {
    configureDay(day) {
        day.isSelected = day.date.getTime() === this.valueTime;
    },
    selectDay(day) {
        this.loadDailyOccurrences(day);
        //this.$emit('input', day.isSelected ? null : day.date);
    },
    loadDailyOccurrences(day) {
      this.daily_loading = true;
      var cur_url = window.location.href
      var cur_host = cur_url.split("/");
      url = cur_host[0] + "//" + cur_host[2] + '/api/atria/calendar/' + this.year + '/' + this.month + '/' + day.day + '/';
      axios
        .get(url)
        .then(response => {
          this.daily_occurrences = response.data.occurrences
        })
        .catch(error => {
          console.log(error)
          this.daily_errored = true
        })
        .finally(() => {
          this.$emit('input', day.isSelected ? null : day.date);
          this.daily_loading = false;
        })
    },
  },
});

Vue.component('multiple-date-picker', {
    created() {
    this.$on('configureDay', this.configureDay);
    this.$on('selectDay', this.selectDay);
  },
  extends: calendar,
  props: {
    value: { type: Array, default: []},
  },
  computed: {
    hasValues() {
        return Array.isArray(this.value) && this.value.length > 0;
    },
    valueTimes() {
        if (!this.hasValues) return [];
      return this.value.map(v => v.getTime());
    },
  },
    methods: {
    configureDay(day) {
        day.isSelected = this.dayIsSelected(day);
    },
    dayIsSelected(day) {
        if (!this.hasValues) return false;
      const t = day.date.getTime();
      return !!this.valueTimes.find(vt => vt === t);
    },
    selectDay(day) {
      if (!day.isSelected) {
        this.$emit('input', this.hasValues ? [...this.value, day.date] : [day.date]);
      } else {
        this.$emit('input', this.value.filter(v => v.getTime() !== day.date.getTime()));
      }
    },
  },
});

Vue.component('date-range-picker', {
    created() {
    this.$on('configureDay', this.configureDay);
    this.$on('selectDay', this.selectDay);
    this.$on('enterDay', this.enterDay);
  },
  extends: calendar,
  data() {
    return {
      valueIsValid: false,
      dragRange: null,
    };
  },
  props: {
    value: { type: Object, default: { } },
  },
  computed: {
    valueIsValid() {
      return this.value && this.value.start && this.value.end;
    },
    normalizedValue() {
      return this.normalizeRange(this.value);
    },
    normalizedDragRange() {
      return this.normalizeRange(this.dragRange);
    },
  },
  watch: {
    normalizedDragRange(val) {
      // Any time drag changes, normalize it and emit 'drag' event
      this.$emit('drag', val ? { start: val.start, end: val.end } : null);
    },
  },
  methods: {
    configureDay(day) {
      const dateTime = day.date.getTime();
      const valueRange = this.normalizedValue;
      const dragRange = this.normalizedDragRange;
        day.isSelected = valueRange && dateTime >= valueRange.startTime && dateTime <= valueRange.endTime;
      day.startsSelection = valueRange && dateTime === valueRange.startTime;
      day.endsSelection = valueRange && dateTime === valueRange.endTime;
      day.dragActive = dragRange; // Just to let day know drag is happening somewhere
      day.isDragged = dragRange && dateTime >= dragRange.startTime && dateTime <= dragRange.endTime;
      day.startsDrag = dragRange && dateTime === dragRange.startTime;
      day.endsDrag = dragRange && dateTime === dragRange.endTime;
    },
    selectDay(day) {
      // Start new drag selection if not dragging
      if (!this.dragRange) {
        this.dragRange = {
          start: day.date,
          end: day.date,
        };
      // Complete drag selection
      } else {
        const { start, end } = this.normalizedDragRange;
        // Clear drag selection
        this.dragRange = null;
        // Signal new value selected on drag complete
        this.$emit('input', { start, end });
      }
    },
    enterDay(day) {
        if (!this.dragRange) return;
      // Update drag selection
      this.dragRange = {
        start: this.dragRange.start,
        end: day.date,
      };
    },
    // Ranges can privately have end date earlier than start date
    // This function will correct the order before exposing it to to other components
    normalizeRange(range) {
      if (!range) return null;
      const { start, end } = range;
      const startTime = start.getTime();
      const endTime = end.getTime();
      const isNormal = start < end;
      return {
        start: isNormal ? start : end,
        startTime : isNormal ? startTime : endTime,
        end: isNormal ? end : start,
        endTime: isNormal ? endTime : startTime,
      };
    }
  },
});

/**************************************************************************************/
/******************** STUFF NEEDED FOR TUTORIAL - NOT FOR REALSIES ********************/
/**************************************************************************************/

const _displayKeyOptions = [
  { id: 'label', value: 'label', label: 'Label' },
  { id: 'number', value: 'day', label: 'Day' },
  { id: 'weekday', value: 'weekday', label: 'Weekday' },
  { id: 'week', value: 'week', label: 'Week' },
  { id: 'month', value: 'month', label: 'Month' },
  { id: 'year', value: 'year', label: 'Year' },
  { id: 'beforeMonth', value: 'beforeMonth', label: 'Before Month' },
  { id: 'afterMonth', value: 'afterMonth', label: 'After Month' },
  { id: 'inMonth', value: 'inMonth', label: 'In Month' },
  { id: 'isToday', value: 'isToday', label: 'Is Today' },
  { id: 'isFirstDay', value: 'isFirstDay', label: 'Is First Day' },
  { id: 'isLastDay', value: 'isLastDay', label: 'Is Last Day' },
];

const _selectModeOptions = [
  { id: 'none', value: 'none', label: 'None' },
  { id: 'single', value: 'single', label: 'Single Date' },
  { id: 'multiple', value: 'multiple', label: 'Multiple Dates' },
  { id: 'range', value: 'range', label: 'Date Range' },
];

const vm = new Vue({
  el: '#cal-app',
  data: {
    displayKeyOptions: _displayKeyOptions,
    displayKey: _displayKeyOptions[1].value,
    selectModeOptions: _selectModeOptions,
    selectMode: _selectModeOptions[1].value,
    showCustomUI: false,
    dateSelection: null,
    dragSelection: null,
    daily_occurrences: null,
    daily_loading: true,
    daily_errored: false,
  },
  computed: {
    datePicker() {
      switch(this.selectMode) {
        case 'single':
          return 'single-date-picker';
        case 'multiple':
          return 'multiple-date-picker';
        case 'range':
          return 'date-range-picker';
        default:
          return '';
      }
    },
    dateSelectionLabel() {
      return JSON.stringify(this.dateSelection, null, '\t');
    }
  },
  watch: {
    selectMode() {
      this.dateSelection = null;
    },
  },
});
