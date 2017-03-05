// ----------------------------------------------------------------------------
// Starting module for lidar maps - sets up global namespace, loads modules,
// and acts as controller, mediating echange of information between modules.
// ----------------------------------------------------------------------------

// Set up a slot for our objects in the global namespace ("window")
var lm = window.lm || {};

// After the document is loaded according to jquery, set up our code.
$(document).ready(function(){

  // Set up configuration information - put anything that is likely to change
  // after the site is up and running here, so we don't have to go fishing through.
  // the code to make changes.
  var config = {
    ajaxUrl: "http://localhost:8080/",
    startingLat: 41.4090,
    startingLon: -75.6624,
    startingZoom: 13
  }

 // Set up starting state - this is a dictionary into which we can put
 // any information that needs to be passed between modules, without creating
 // global variables.
  var state = { };

// This is the function the map will call when anything in the state changes.
// Note that the map can update the UI, zoom or pan or do anything else without
// changing the state.  State changes are just for those changes that need to
// be reflected in actions taken by other modules.  Currently these are
// called explicitly but we can change this to be generic if we have many modules
  var mapCallback = function(state){
   lm.example.update(state);
  }

  var exampleCallback = function(state){
   lm.map.update(state);
  }

 // This creates a variable representing the modules and all the functions we
 // need to manipulate them, stored for example in map.js.  After it is loaded,
 // our namespace, window.lm, should contain a reference to an object
 // called lmap, accessed via lm.lmap.  The jquery when function lets
 // you load multiple modules, and executes the done() function only after
 // all the modules are loaded.  This lets our js app be referenced only by
 // lildar_maps.js in the html, while in fact it contains several modules
 // containing objects that are isolated into the lm namespace.
 $.when(
    $.getScript( "js/map.js" ),
    $.getScript( "js/example.js" ),
    // ******* TODO - add modules here as needed, for example, for town
    // selector/autocomplete, or others as needed. *******
    $.Deferred(function( deferred ){
        $( deferred.resolve );
    })
 ).done(function(){
    // Now we have an lmap in our namespace, and can access its functions.
    lm.lmap.init(config, state, mapCallback);
    lm.example.init(config, state, exampleCallback);
    // ******* TODO -initialize other modules similarly. *******
  });
});
