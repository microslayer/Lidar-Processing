// When the file is loaded it creates a new object in the lm namepace representing the map.
// Loading this via the jquery."when" function.  The new keyword here creates a new instance
// of the function, with a newly-created value of "this", which means it functions more like
// a normal class in other languages, where multiple instances of the class can be created.
// There are many opinions on how best to to this - see this discussion for example:
// http://stackoverflow.com/questions/9782379/deathmatch-self-executing-anonymous-function-vs-new-function
lm.lmap =  new function () {
  // "this" refers to the current function.  Since we need to access it from
  // other functions, which also have their own "this", we need to save it
  // in a local variable.
  var that = this;
  var map = null;

  // We keep these variables private inside this curent "closure" scope.
  // using "this.ini" let's us access init() from outside this module, as
  // long as we have a reference to "this".
  this.init = function(cfg, state, callback){
     // The initial setup needs to save these paramters for future use,
     // in the pointer to the containing object/function, "that":
     that.notify = callback;
     that.state = state;
     that.ajaxUrl = cfg.ajaxUrl;
     // L is a global used by leaflet.  We can create the new leaflet map
     // by passing in the div id into which we want to display the map.
     map = L.map('map');
     map.setView([cfg.startingLat, cfg.startingLon], cfg.startingZoom);
     var mapLayer = L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}.png', {
          minZoom: 5, maxZoom: 19
     });
     mapLayer.addTo(map);

    // When the user clicks on the map, we want to take some action.
    map.on("click", function(e){
        // For now, we can just call the example service endpoint.  Note that
        // this needs to be up and running locally.  You can run it by
        // going to the services directory and running "python server.py".
        // Note the second parameter, which is the function to execute after
        // the ajax call is complete.  ******* TODO: This needs to be changed to the
        // actual service call that needs to run on click. *******
        $.get( that.ajaxUrl + "/example?lat=" + e.latlng.lat + "&lon=" + e.latlng.lng, display, dataType="json");
    });
  };

  // Function that is called after the ajax call is complete.  Data contains
  // a json obect representing the server's json response.  ******* TODO: This
  // needs to be changed to display the geojson coming back from the service
  // as well as the number of tiles and town name.
  // Note that in functions defined as objects, "this." is public; "var" is private.
  var display = function(data){
    that.state.localityName = "Scranton, PA"
    that.state.tileCount = "25"
    alert(JSON.stringify(data, 4));
    that.notify(that.state); 
  };

  this.update = function(newState){
    console.log("Example updated");
    that.state = newState;
    console.log(that.state);
  };
};
