lm.example =  new function () {
  var that = this;

  this.init = function(cfg, state, callback){
     that.notify = callback;
     that.state = state;
     that.ajaxUrl = cfg.ajaxUrl;
  };

  // TODO: Add functions as needed here to get data from the services and to
  // update the user interface. When the other modules need to be updated,
  // update the state and call that.notify with it. See map.js for a more
  // detailed example.

  // Called when this module needs to be updated with a new state.
  this.update = function(newState){
    console.log("Example updated");
    that.state = newState;
    console.log(that.state);
  };
};
