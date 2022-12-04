'use strict';
import pusher-js/node
const Pusher = require('pusher');

// Open a Pusher connection to the Realtime Reddit API
var pusher = new Pusher("50ed18dd967b455393ed");

// Subscribe to the /r/AskReddit subreddit (lowercase)
var subredditChannel = pusher.subscribe("askreddit");

// Listen for new stories
subredditChannel.bind("new-listing", function(listing) {
// Output listing to the browser console
console.log(listing);
});