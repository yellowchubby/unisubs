// Amara, universalsubtitles.org
//
// Copyright (C) 2013 Participatory Culture Foundation
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see
// http://www.gnu.org/licenses/agpl-3.0.html.

(function() {

    var root = this;

    var VideoController = function($scope, SubtitleStorage) {
        /**
         * Responsible for initializing the video and all video controls.
         * @param $scope
         * @param SubtitleStorage
         * @constructor
         */

        // The Popcorn instance.
        //
        // For now, make sure we force controls.
        $scope.pop = window.Popcorn.smart('#video', SubtitleStorage.getVideoURL() + '&controls=1');

        $scope.playChunk = function(start, duration) {
            // Play a specified amount of time in a video, beginning at 'start',
            // and then pause.

            // Pause the video, first.
            $scope.pop.play();

            // Remove any existing cues that may interfere.
            $scope.removeAllTrackEvents();

            if (start < 0) {
                start = 0;
            }

            // Set the new start time.
            $scope.pop.currentTime(start);

            // Set a new cue to pause the video at the end of the chunk.
            $scope.pop.cue(start + duration, function() {
                $scope.pop.pause();
            });

            // Play the video.
            $scope.pop.play();

        };
        $scope.removeAllTrackEvents = function() {

            var trackEvents = $scope.pop.getTrackEvents();
            for (var i = 0; i < trackEvents.length; i++) {
                $scope.pop.removeTrackEvent(trackEvents[i].id);
            }

        };
        $scope.togglePlay = function() {

            // If the video is paused, play it.
            if ($scope.pop.paused()) {
                $scope.pop.play();

            // Otherwise, pause it.
            } else {
                $scope.pop.pause();
            }

        };
    };

    root.VideoController = VideoController;

}).call(this);
