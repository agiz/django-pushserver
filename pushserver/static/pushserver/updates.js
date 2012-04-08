var updatesProcessors = {};

function registerUpdatesProcessor(type, processor) {
	if (updatesProcessors[type]) {
		updatesProcessors[type].push(processor);
	}
	else {
		updatesProcessors[type] = [processor];
	}
}

function processUpdate(data) {
	processors = updatesProcessors[data.type];
	if (processors) {
		jQuery.each(processors, function (i, processor) {
			processor(data);
		});
	}
}

function listenForUpdates() {
	function listen(last_modified, etag) {
		function delayedListen(new_last_modified, new_etag) {
			setTimeout(function () {
				listen(new_last_modified || last_modified, new_etag || '0');
			}, 1000); // 1 second delay
		}

		function warn(message) {
			if ((typeof window.console != "undefined") && (typeof window.console.warn == "function")) {
				window.console.warn(message);
			}
		}

		var xmlhttp;
		if (window.XMLHttpRequest) {
			xmlhttp=new XMLHttpRequest();
		}
		else {
			xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
		}

        xmlhttp.onreadystatechange=function()
        {
			if ( xmlhttp.readyState==4 && xmlhttp.status==200 )
			{
				var new_last_modified = xmlhttp.getResponseHeader('Last-Modified');
				try {
					var new_etag = xmlhttp.getResponseHeader('Etag');
					if (new_etag === null) throw null;
				}
				catch (e) {
					try {
						// Chrome and other WebKit-based browsers do not (yet) support access to Etag
						// so we try to find the same information in the Cache-Control field
						new_etag = (/etag=(\S+)/.exec(xmlhttp.getResponseHeader('Cache-Control')))[1];
					}
					catch (e) {}
				}
				
				data = jQuery.parseJSON(eval(xmlhttp.responseText));

				if (new_last_modified === null) {
					warn("Last-Modified field is not available");
				}
				if (new_etag === null) {
					warn("Etag field is not available");
				}

				if (!data) {
					warn("No data in push request");
				}
				else {
					processUpdate(data);
				}

				if ((new_last_modified !== null) && (new_etag !== null)) {
					listen(new_last_modified, new_etag);
					return;
				}
				else {
					// TODO: Should we handle the error in some other manner?
					delayedListen(new_last_modified, new_etag);
					return;
				}
			}
        }

        xmlhttp.open('GET', updates_url, true);
		xmlhttp.setRequestHeader("If-None-Match", etag);
		xmlhttp.setRequestHeader("If-Modified-Since", last_modified);
        xmlhttp.send(null);
	}
	listen('Thu, 1 Jan 1970 00:00:00 GMT', '0');
}

jQuery(document).ready(function () {
	listenForUpdates();
});