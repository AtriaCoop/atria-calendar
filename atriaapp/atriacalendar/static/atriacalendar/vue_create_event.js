/***************************************************/
/********  BASE EVENT CREATION COMPONENT ***********/
/***************************************************/

const eventForm = new Vue({
  el: '#event-form',
  data: {
    title: '',
    description: '',
    datetime: new Date(),
    location: '',
    opportunities: []
  },
  computed: {
    localeTimeString: {
      get: function () {
        return this.datetime.toTimeString().slice(0, 5);
      },
      set: function (newValue) {
        const splitTime = newValue.split(':');

        this.datetime = new Date(this.datetime.toISOString());
        this.datetime.setHours(splitTime[0]);
        this.datetime.setMinutes(splitTime[1]);
      }
    },
    localeTimeString12h: function () {
      return this.datetime.toLocaleTimeString().replace(/:\d{2} /, ' ');
    },
    localeDateString: {
      get: function () {
        return this.datetime.toISOString().split('T')[0];
      },
      set: function (newValue) {
        this.datetime = new Date(this.datetime.toISOString());
        this.datetime.setFullYear(newValue.getUTCFullYear());
        this.datetime.setDate(newValue.getUTCDate());
        this.datetime.setMonth(newValue.getUTCMonth());
      }
    }
  }
});
