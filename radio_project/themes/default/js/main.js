var enable_news_comments_nesting = true;
var lastplayed_page = 1;
var djmode = 0;

function log(msg) {
	setTimeout(function(){
		throw new Error(msg);
	}, 0);
}
String.prototype.format = function() {
	var args = arguments;
	return this.replace(/{(\d+)}/g, function(match, number) { 
		return typeof args[number] != 'undefined'
		? args[number]
		: match
		;
	});
};
function gup(name) {
  name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
  var regexS = "[\\?&]"+name+"=([^&#]*)";
  var regex = new RegExp( regexS );
  var results = regex.exec( window.location.href );
  if( results == null )
    return "";
  else
    return results[1];
}
function fix_url () {
	target = location.pathname;
	switch (target) {
		case "/news/":
			url = "#/news/{0}/";
			nid = gup("nid");
			if (nid == "") {
				url = "#/news/";
			}
			else {
				url = url.format(nid);
			}
			break;
		case "/lastplayed/":
			url = "#/lastplayed/{0}/";
			sort = gup("sort");
			if (sort == "") {
				url = "#/lastplayed/";
			}
			else {
				url = url.format(sort);
			}
			break;
		case "/queue/":
			url = "#/queue/";
			break;
		case "/submit/":
			url = "#/submit/";
			break;
		case "/staff/":
			url = "#/staff/";
			break;
		case "/irc/":
			url = "#/irc";
			break;
		case "/stats/":
			url = "#/stats";
			break;
		case "/favorites/":
			url = "#/favorites/{0}";
			nick = gup("nick");
			if(nick != "") {
				url = url.format(nick);
				fave_nick = nick;
			}
			else {
				url = "#/favorites";
			}
			break;
		case "/search/":
			url = "#/search/{0}/{1}";
			page = gup("page");
			if (page == "") {
				page = "1";
			}
			query = gup("query");
			if (query != "") {
				url = url.format(page, query);
			}
			else {
				url = "#/search/";
			}
			break;
		default:
			url = false;
	}
	if (url != false) {
		location = "http://" + location.hostname + "/" + url;
	}
}
//fix_url();
var sync_seconds = 0;
var search_query = "";
var search_page = "1";
var search_pages = "1";
var counter = 0.0;
var counter_search = 0.0;
var update_progress = 0.0;
var update_progress_inc = 0.0;
var update_old_progress = 0.0;
var update_lp = "";
var update_queue = "";
var lastplayed_order = "";
var current_pos = 0;
var current_len = 0;
var fave_nick = "";
function get_page(page, url, finish, postprocess) {
	if (!finish) {
		finish = function () { };
	}
	if (url == false) {
		if (page == "p-staff") {
			url = "/staff/staff.php";

			if (djmode==6) url = "/staff/eggstaff.php"; //egg

			finish = function () {
				$("#page-p-staff .djinfo").twipsy({animate: true, placement: "below", trigger: "hover", fallback: "Default"});
			};
		}
		else if (page == "p-home") {
			url = "/home.php";
			finish = function () {
				setInterval(periodic, 500);
				$.ajax({
					url: "/relay/api.php",
					type: "GET",
					dataType: 'jsonp',
					data: "min_bitrate=128&active=1&not_full=1",
					success: function (resp) {
						var mp3index = -1;
						var oggindex = -1;
						var mp3ratio = 1;
						var oggratio = 1;
						sources = {};
						for(var i in resp) {
							var listeners = parseInt(resp[i]['listeners']);
							var limit = resp[i]['listener_limit'];
							if(limit == null)
								limit = 600;
							else
								limit = parseInt(limit);
							if(resp[i]['format'] == 'mp3' && (mp3index == -1 || listeners/limit < mp3ratio)) {
								mp3index = i;
								mp3ratio = listeners/limit;
							}
							if(resp[i]['format'] == 'ogg' && (oggindex == -1 || listeners/limit < oggratio)) {
								oggindex = i;
								oggratio = listeners/limit;
							}
						}
						if(oggindex != -1)
							sources['oga'] = "http://{0}.r-a-d.io:{1}{2}?_t={3}".format(resp[oggindex]['relay_name'], resp[oggindex]['port'], resp[oggindex]['mount'], Math.round(new Date().getTime()/1000.0));
						if(mp3index != -1)
							sources['mp3'] = "http://{0}.r-a-d.io:{1}{2}?_t={3}".format(resp[mp3index]['relay_name'], resp[mp3index]['port'], resp[mp3index]['mount'], Math.round(new Date().getTime()/1000.0));
						$("#player").jPlayer({
							ready: function () {
								$(this).jPlayer("setMedia", sources);
								$(".jp-play").attr("disabled", false);
							},
							supplied: Object.keys(sources).join(", "),
							//supplied: "oga, mp3",
							swfPath: window.swfpath,
							cssSelectorAncestor: "#streamconnect"
						});
						
						
					}
				});
				$("#search").submit(search_submit);
			};
		}
		else if (page == "p-lastplayed") {
			url = "/lastplayed/lp.php";
			finish = lastplayed_bind;
		}
		else if (page == "p-queue") {
			url = "/queue/queue.php";
			finish = function () {
				update_queue = $("#page-p-queue table tbody tr").first().children("td").first().text();
			}
		}
		else if (page == "p-search") {
			url = "/search/search.php";
			finish = function () {
				search_pagination();
			}
		}
		else if (page == "p-irc") {
			url = "/irc/irc.php";
		}
		else if (page == "p-submit") {
			url = "/submit/submit.php";
			finish = submit_bind;
		}
		else if (page == "p-news") {
			url = "/news/news.php";
			finish = function () {
				news_bindings();
			}
		}
		else if (page == "p-stats") {
			url = "/stats/stats.php";
		}
		else if (page == "p-favorites") {
			url = "/favorites/favorites.php";
			finish = function() {
				faves_bind();
			}
		}
	}
	if (url != false) {
		clear_error_view();
		$.ajax({
				method: "get",
				url: url,
				dataType: 'text',
				success: function (resp) {
					$("#page-{0}".format(page)).remove();
					$("body").append('<div class="container page" id="page-{0}" style="display: none;">'.format(page));
					$("body").append($("#info-footer"));
					$("#page-{0}".format(page)).append(resp);
					finish();
					$(".page").hide();
					$("#page-{0}".format(page)).slideDown();
					var matchstr = page.substring(2, page.length);
					var piwikurl = "/";
					if(matchstr != "home")
						piwikurl += matchstr;
					if(matchstr == "search")
						piwikurl += (search_query=="" ? "" : "/") + search_query;
					if(matchstr == "favorites")
						piwikurl += (fave_nick=="" ? "" : "/") + fave_nick;
					piwikTracker.setCustomUrl(piwikurl);
					piwikTracker.trackPageView(matchstr);
					if (postprocess === undefined);else {
						postprocess();
					}
				}});
	}
	else {
		error_view("URL generation is broken, please try a different button");
	}
}
function fetch_news(nid) {
	$.ajax({
			method: 'get',
			url: '/news/api.php?nid={0}'.format(nid),
			dataType: 'jsonp',
			success: function (resp) {
				$("#page-p-news .news").hide();
				element = $("#page-p-news .news[value={0}]".format(resp.nid));
				$("#page-p-news .news[value={0}] h5 a".format(resp.nid)).addClass("active_item");
				element.show().children().not("h5").remove();
				content_html = '<div class="well content"><div class="nw_time">{1}</div>{0}</div>'
				element.append(content_html.format(resp.content[0], resp.content[1]));
				element.append(resp.reply);
				if (resp.pub) {
					Recaptcha.create(resp.pub, "captcha", {
							theme: 'white',
							callback: Recaptcha.focus_response_field
						}
					);
				}
				else {
					$("#captcha").html("Logged in, no captcha required.");
				}
				comment_html = '<div class="comment well" id="cmt{0}"><div class="cmt_head"><a class="cmt_name"{2}>{1}</a> #{0} {3}<span class="cmt_time">{4}</span></div><div class="cmt_text">{5}</div></div>';
				$.each(resp.comments, function (i, item) {
					if (item[1] == "") {
						item[1] = "Anonymous";
					}
					if (item[3] != "") {
						item[3] = '<abbr title="This was posted by {0}.">&#9733;</abbr>'.format(item[3]);
					}
					if (item[2] != "") {
						item[2] = ' href="mailto:{0}"'.format(item[1]);
					}
					element.append(comment_html.format(item[0], item[1], item[2], item[3], item[4], item[5]));
				});
				comment_bind();
				chanify();
			}
		});
}
function fetch_lastplayed(page, order) {
	$.ajax({
			method: 'get',
			url: '/lastplayed/api.php?page={0}&sort={1}'.format(page, order),
			dataType: 'jsonp',
			success: function (resp) {
				if (resp.length > 0) {
					tbody = $("#page-p-lastplayed table tbody");
					tbody.empty();
					$("#page-p-lastplayed .row").show();
					$("#page-p-lastplayed .alert-message").hide();
					html_row = '<tr><th>{0}</th><td>{1}</td><td>{2}</td><td>{3}</td></tr>';
					$.each(resp, function (i, item) {
						tbody.append(html_row.format(item[0], item[1], item[2], item[3]));
					});
					$('#paginpn').html(lastplayed_page<2?'x':lastplayed_page-1);
					$('#paginnn').html(lastplayed_page+1);
				}
				else {
					$("#page-p-lastplayed table tbody").empty();
					$("#page-p-lastplayed .alert-message").show();
					$("#page-p-lastplayed .row").show();
				}
			}});
}
function fetch_queue() {
	$.ajax({
			method: 'get',
			url: '/queue/api.php',
			dataType: 'jsonp',
			success: function (resp) {
				if (resp.length > 0) {
					tbody = $("#page-p-queue table tbody");
					tbody.empty();
					$("#page-p-queue .row").show();
					$("#page-p-queue .alert-message").hide();
					html_row = '<tr><th>{0}</th><td>{1}</td></tr>';
					$.each(resp, function (i, item) {
						text = item[1];
						if(item[2] == 1)
							text = "<b>" + text + "</b>";
						tbody.append(html_row.format(timeConverter(item[0]), text));
					});
				}
				else {
					$("#page-p-queue table tbody").empty();
					$("#page-p-queue .alert-message").show();
					$("#page-p-queue .row").hide();
				}
			}
		});
}
commenttext = ""; // bah how hacky
function comment_bind() {
	$("#comment-form").ajaxForm({
		beforeSubmit: function (formData, jqForm, options) {
			commenttext = $('#comment-form textarea').val();
		},
		success: function (resp) {
			result = $(resp).children("h2").text();
			$("#comment_info .modal-body").empty();
			$("#comment_info .modal-body").html('<p>{0}</p>'.format(result));
			$("#comment_info").modal({keyboard: true, backdrop: true, show: true});
			fetch_news($(".active_item").parentsUntil(".news").parent().attr("value"));
			if(!result.match("Thank .*")) {
				$('#comment-form textarea').val(commenttext);
			}
		}
	});
}
function submit_bind() {
	$("#submit-form-main form").ajaxForm({
		success: function (resp) {
			result = $(resp).children("h2").text();
			$("#submit_info .modal-body").empty();
			$("#submit_info .modal-body").html('<p>{0}</p>'.format(result));
			$("#submit_info").modal({keyboard: true, backdrop: true, show: true});
			if (!result.match("Error:.*")) {
				$("#page-p-submit .alert-message").removeClass("success").addClass("danger").children("p").text("You need to wait another 60 minutes before uploading again.");
			}
			$("#submit-form-main .input-e").show();
			$("#submit_uploading").hide();
		},
		beforeSubmit: function (formData, jqForm, options) {
			$("#submit-form-main .input-e").hide();
			$("#submit_uploading").show();
			if($(".replace-song input:checked").first()[0] != $(".replace-song input").first()[0])
				$(".replace-song input:checked").parent().parent().remove();
			$(".replace-song input").first().prop('checked', true);
		},
		error: function (jqXHR, textStatus, errorThrown) {
			$("#submit-form-main .input-e").show();
			$("#submit_uploading").hide();
			$("#submit_info .modal-body").empty();
			$("#submit_info .modal-body").html('<p>An error occured: {0}</p>'.format(textStatus));
			$("#submit_info").modal({keyboard: true, backdrop: true, show: true});
		}
	});
}
function faves_bind() {
	$("#page-p-favorites tbody .fave-request").parent().submit(function () {
		songid = $(this).children().first().attr("value");
		$.ajax({
			url: "/request/index.py",
			type: "POST",
			data: "songid={0}".format(songid),
			success: function (resp) {
				$("#page-p-favorites .fave-request").attr('disabled', 'disabled')
				$("#page-p-favorites .fave-request").removeClass('info');
				$("#page-p-favorites .fave-request").addClass('warning');
				result = $(resp).children("h2").text();
				$("#faves_request_info .modal-body").empty();
				$("#faves_request_info .modal-body").html('<p>{0}</p>'.format(result));
				$("#faves_request_info").modal({keyboard: true, backdrop: true, show: true});
			}
		});
		return false;
	});
	$("#page-p-favorites tbody .fave-delete").parent().submit(function () {
		elem = $(this);
		faveid = $(this).children().first().attr("value");
		$.ajax({
			url: "/favorites/favorites.php",
			type: "POST",
			data: "delfave={0}".format(faveid),
			success: function (resp) {
				elem.parent().parent().remove();
			}
		});
		return false;
	});
	$("#page-p-favorites #nicksearch").submit(function() {
		fave_nick = $("#page-p-favorites #nicksearch input[type=text]").attr("value");
		window.location.hash = "#/favorites/{0}".format(fave_nick);
		get_page("p-favorites", "/favorites/favorites.php?nick={0}".format(fave_nick), function() {
			faves_bind();
		});
		return false;
	});
	$("#page-p-favorites #login-fave").submit(function() {
		nickname = $("#page-p-favorites #login-fave input[name=nickname]").attr("value").trim();
		authcode = $("#page-p-favorites #login-fave input[name=authcode]").attr("value").trim();
		if(nickname == "" || authcode == "") {
			return false;
		}
		$.ajax({
			url: "/favorites/favorites.php",
			type: "POST",
			data: "login=submit&nickname={0}&authcode={1}".format(nickname, authcode),
			success: function (resp) {
				get_page("p-favorites", "/favorites/favorites.php?nick={0}".format(fave_nick), function() {
					faves_bind();
					$("#nicksearch").prepend(resp);
				});
			}
		});
		return true;
	});
	$("#page-p-favorites #logout-fave").submit(function() {
		$.ajax({
			url: "/favorites/favorites.php",
			type: "POST",
			data: "logout=submit",
			success: function (resp) {
				get_page("p-favorites", "/favorites/favorites.php?nick={0}".format(fave_nick), function() {
					faves_bind();
				});
			}
		});
		return false;
	});
}
function lastplayed_bind() {
	if (djmode==6) //egg
	{
		loadgif = '/css/loadegg.gif';
		pacrun(0);
	}

	update_lp = $("#page-p-lastplayed table tbody tr").first().children("td").first().text();
	$("#page-p-lastplayed table thead th > a").each(function (i) {
		list = ['#/lastplayed/', '#/lastplayed/play/', '#/lastplayed/fave/'];
		clicks = [function () {
			lastplayed_order = "";
			fetch_lastplayed(lastplayed_page, lastplayed_order);
		}, function () {
			lastplayed_order = "play";
			fetch_lastplayed(lastplayed_page, lastplayed_order);
		}, function () {
			lastplayed_order = "fave";
			fetch_lastplayed(lastplayed_page, lastplayed_order);
		}];
		$(this).attr('href', list[i]);
		$(this).click(clicks[i]);
	});
}
function search_pagination() {
	target = parseInt(search_page);
	$(".page-browse .next").click(function () {
		if ((parseInt(search_page) + 1) <= search_pages) {
			search_submit(parseInt(search_page) + 1, false);
		}
	});
	$(".page-browse .prev").click(function () {
		if (((parseInt(search_page) - 1) < search_pages) && ((parseInt(search_page) - 1) > 0)) {
			search_submit(parseInt(search_page) - 1, false);
		}
	});
	$(".page-browse li").not(".prev, .next, .active").children().click(function () {
		if (parseInt(search_page) != parseInt($(this).text())) {
			search_submit(parseInt($(this).text()), false);
		}
	});
	$(".alphanum a").unbind("click");
	$(".alphanum a").click(function() {
		$("#search input:text").first().val("alphanum:" + $(this).text());
		return search_submit("1");
	});
	request_binds();
}
function request_binds() {
	$("#page-p-search tbody button").click(function () {
		songid = $(this).attr("value");
		$.ajax({
			url: "/request/index.py",
			type: "POST",
			data: "songid={0}".format(songid),
			success: function (resp) {
				result = $(resp).children("h2").text();
				$("#request_info .modal-body").empty();
				$("#request_info .modal-body").html('<p>{0}</p>'.format(result));
				$("#request_info").modal({keyboard: true, backdrop: true, show: true});
				search_submit(search_page, false);
				counter_search = 0;
			}
		});
	});
}
function search_submit(search_page, focus) {
	match = $("#page-p-search");
	search_query = $("#search input:text").first().val();
	if (!search_page) {
		search_page = "1";
	}
	if (focus != false) {
		focus = true;
	}
	if (match.length == 0) {
		$(".topbar .nav li").removeClass("active");
		$("#p-search").addClass("active");
		$(".page").hide();
		window.location.hash = "#/search/{1}/{0}".format(search_query, search_page);
		get_page("p-search", '/search/search.php?query={0}&page={1}&update={2}'.format(search_query, search_page, focus == true ? '1' : '0'), function () {
			$("#request_info").modal({keyboard: true});
			search_pagination();
		});
		//if(search_query != "" && focus == true) {
		//	piwikTracker.setCustomUrl("/search/" + search_query);
		//	piwikTracker.trackPageView("search");
		//}
	}
	else {
		clear_error_view();
		if (focus) {
			window.location.hash = "#/search/{1}/{0}".format(search_query, search_page);
		}
		$.ajax({
				method: 'get',
				url: '/search/api.php?query={0}&page={1}&update={2}'.format(encodeURI(search_query), search_page, focus == true ? '1' : '0'),
				dataType: 'jsonp',
				success: function (resp) {
					if(search_query != "" && focus == true) {
						piwikTracker.setCustomUrl("/search/" + search_query);
						piwikTracker.trackPageView("search");
					}
					if ($.isEmptyObject(resp) != true) {
						if (focus == true) {
							$(".go").removeClass("active");
							$(".go#p-search").addClass("active");
							$(".page").hide();
							$("#page-p-search").slideDown();
							$("#results").prevUntil("#search_welcome").last().prev().hide();
							$("#results").show();
						}
						$("#request_status").removeClass("danger").removeClass("success").addClass(resp.status ? "success" : "danger");
						$("#request_status > p").html(resp.cooldown);
						$("#results tbody").empty();
						html_row = '<tr><td>{0}<b>{1}</b></td><td>{2}</td><td>{3}</td><td><button {5}class="btn {6}" value="{4}">Request</a></button></td></tr>';
						$.each(resp.result, function (i, item) {
							if (item[5] == false) {
								btn_disabled = "";
								btn_disable = 'info';
							}
							else {
								btn_disabled = 'disabled="disabled" ';
								btn_disable = 'warning disabled';
							}
							if (item[0] != "") {
								item[0] = item[0] + " - ";
							}
							$("#results tbody").append(html_row.format(item[0], item[1], timeConverter(item[2], 10), timeConverter(item[3], 10), item[4], btn_disabled, btn_disable));
						});
						html_prev = '<li class="prev {0}"><a href="#/search/{1}/{2}">&larr; Previous</a></li>';
						if (resp.page > 1) {
							html_prev = html_prev.format("", resp.page - 1, search_query);
						}
						else {
							html_prev = html_prev.format("disabled", resp.page - 1, search_query);
						}
						$(".page-browse ul").html(html_prev);
						html_pagination = '<li {1}><a href="#/search/{2}/{3}">{0}</a></li>';
						for (inc = 1; inc <= resp.pages; inc++) {
							if (inc == resp.page) {
								$(".page-browse ul").append(html_pagination.format(inc, 'class="active"', resp.page, search_query));
							}
							else {
								$(".page-browse ul").append(html_pagination.format(inc, "", inc, search_query));
							}
						}
						html_next = '<li class="next {0}"><a href="#/search/{1}/{2}">Next &rarr;</a></li>';
						if (resp.page < resp.pages) {
							html_next = html_next.format("", resp.page + 1, search_query);
						}
						else {
							html_next = html_next.format("disabled", resp.page + 1, search_query);
						}
						$(".page-browse ul").append(html_next);
						window.search_page = resp.page;
						search_pages = resp.pages;
						search_pagination();
					}
					else {
						if (focus == true) {
							$(".go").removeClass("active");
							$(".go#p-search").addClass("active");
							$(".page").hide();
							$("#page-p-search").slideDown();
							$("#results").prev().show();
							$("#results").hide();
						}
						$("#results tbody").empty();
					}
			}
		});
	}
	return false;
}
function update_periodic() {
	if (djmode==6 || djmode==20) {
		uri = '/api.php?lp=1&modo=egg';
	} else {
		uri = '/api.php?lp=1&q=1';
	}
	$.ajax({
			method: 'get',
			url: uri,
			dataType: 'jsonp',
			success: function (resp) {
				if (resp.online == 1) {
					apply_playing(resp.np);
					apply_listeners(resp.list);
					apply_bitrate(resp.kbps);
					apply_djimg(resp.djimg);
					apply_dj(resp.dj, resp.djtext);
					apply_list("last-played", resp.lp);
					apply_list("queue", resp.queue);
					parse_progress(resp.start, resp.end, resp.cur);
					if (($("#page-p-lastplayed").length > 0) && (update_lp != resp.lp[0][1])) {
						fetch_lastplayed(lastplayed_page, lastplayed_order);
						update_lp = resp.lp[0][1];
					}
					if ($.isEmptyObject(resp.queue) != true) {
						if (($("#page-p-queue").length > 0) && (update_queue != resp.queue[0][1])) {
							fetch_queue();
							update_queue = resp.queue[0][1];
						}
					}
					apply_thread(resp.thread);
				}
				else {
					apply_thread(0);
					apply_dj("None");
					apply_djimg("/res/img/dj/none.png");
					apply_playing("STREAM IS CURRENTLY DOWN");
					apply_bitrate("0");
					apply_listeners("0");
					apply_list("queue", null);
					apply_list("last-played", resp.lp);
					parse_progress(0, 0, 0);
				}
			}
		});
}
function timeConverter(UNIX_timestamp, mode){
	if (UNIX_timestamp == "Never") {
		return UNIX_timestamp;
	}
	// else if (mode == 10) {  // reverted this since it breaks layout + looks pretty bad overall - Vin
		// var a = new Date(UNIX_timestamp*1000);
		// return a.toLocaleString();
	// }
	var a = new Date(UNIX_timestamp*1000);
	var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
	var days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
	var year = a.getFullYear();
	var month = months[a.getMonth()];
	var day = days[a.getDay()];
	var date = a.getDate();
	var hour = a.getHours();
	var min = a.getMinutes();
	var sec = a.getSeconds();
	if (mode == 10) {
		var time = day+' '+date+' '+month+', '+(hour<10?'0':'')+hour+':'+(min<10?'0':'')+min;
	}
	else if (mode) {
		var time = +(min<10?'0':'')+min+':'+(sec<10?'0':'')+sec;
	}
	else {
		var time = +(hour<10?'0':'')+hour+':'+(min<10?'0':'')+min+':'+(sec<10?'0':'')+sec;
	}
	return time;
}
function apply_list(which, list) {
	html_row = "<tr><th>{0}</th><td>{1}</td></tr>";
	if (list == null) {
		$("#{0}".format(which)).parent().hide();
		match = $(".span8 > #queue:visible, .span8 > #last-played:visible");
		if (match.length == 1) {
			match.parent().removeClass("span8").addClass("span16");
		}
		else if (match.length == 0) {
			match2 = $(".span16 > #queue:visible, .span16 > #last-played:visible");
			if (match2.length == 2) {
				$.each(match2, function () {
					$(this).parent().removeClass("span16").addClass("span8").show();
				});
			}
		}
	}
	else {
		$(".span16 > #queue:visible, .span16 > #last-played:visible").parent().removeClass("span16").addClass("span8");
		$("#{0}".format(which)).parent().show();
		inc = 0;
		pos = 0;
		$("#{0} tbody".format(which)).empty();
		$.each(list, function (i, item) {
			//time = timeConverter(item[0] + sync_seconds);
			time = new Date(item[0]*1000);
			//time = time.toLocaleTimeString();
			time = time.toTimeString().split(' ')[0];
			text = item[1];
			if(item[2] == 1) {
				text = "<b>" + text + "</b>";
			}
			$("#{0} tbody".format(which)).append(html_row.format(time, text));
		});
	}
}
function apply_thread(thread) {
	if (thread != 0) {
		$("#thread").html('We currently have a thread up! <a href="#" target="_blank">Join us here.</a>');
		$("#thread a").attr("href", thread);
	}
	else {
		$("#thread").html('From time to time we have a thread up on /a/. This however, is no such time.');
	}
}
function apply_dj(dj, djtext) {
	$("#page-p-home #dj").html(dj);
	if (!djtext) {
		djtext = "Nothing";
	}
	$("#page-p-home .djmedia").attr("data-original-title", djtext);
}
function apply_djimg(djimg) {
	$("#page-p-home .djimg").attr("src", djimg);
}
function apply_playing(playing) {
	$(".nowplaying h2").html(playing);
}
function apply_listeners(listeners) {
	$(".listeners .value").html(listeners);
}
function apply_bitrate(bitrate) {
	//$(".bitrate .value").html(bitrate);
}
function parse_progress(start, end, cur) {
	if (end != 0) {
		cur_time = Math.round(new Date().getTime()/1000.0);
		sync_seconds = cur_time - cur;
		end += sync_seconds;
		start += sync_seconds;
		temp_update_progress = 0;
		duration = end - start;
		position = cur_time - start;
		update_progress = 100 / duration * position;
		update_progress_inc = 100 / duration * 0.5;
		current_pos = position;
		current_len = duration;
	}
	else {
		update_progress = false;
	}
}
function SecondsToReadable(seconds) {
        var hours = Math.floor(seconds / 3600);
        var mins = Math.floor((seconds % 3600) / 60);
        var secs = Math.floor((seconds % 3600) % 60);
        return (hours > 0 ? +(hours<10?'0':'')+hours+':' : '')+(mins<10?'0':'')+mins+':'+(secs<10?'0':'')+secs;
}
function apply_progress() {
	if (update_progress != false) {
		if ((update_progress < update_old_progress) || (update_old_progress == false)) {
			update_progress += update_progress_inc;
			$("#progress .progress").removeClass("danger").addClass("info");
			$("#progress .progress .bar").css({width: "{0}%".format(update_progress)});
		}
		else {
			update_progress += update_progress_inc;
			$("#progress .progress").removeClass("danger").addClass("info");
			$("#progress .progress .bar").css({width: "{0}%".format(update_progress)});
		}
		// Fill the duration counter
			$("#current_pos").html(SecondsToReadable(current_pos));
			$("#current_len").html(SecondsToReadable(current_len));
	}
	else {
		$("#progress .progress").addClass("danger").removeClass("info");
		$("#progress .progress .bar").css({width: "100%"})
		// Empty the duration counter
		$("#current_pos").empty();
		$("#current_len").empty();
	}
	update_old_progress = update_progress;
}
function fpnews_bindings() {
	$(".news h5 a").each(function () {
		$(this).click(function () {
			var npid = '' + $(this).attr('alt');
			get_page('p-news','/news/news.php',null,function() {
				log('daisychaining #'+npid);
				news_bindings();
				fetch_news(npid);
				$(".go").removeClass("active");
				$(".go#p-news").addClass("active");
			});
		});
		$(this).attr("href", '#/news/'+$(this).attr("alt"));
	});
}
function news_bindings() {
	$("#page-p-news .news h5 a").each(function () {
		$(this).click(function () {
			$("#page-p-news").next("iframe").remove();
			if ($(this).hasClass("active_item")) {
				$(this).removeClass("active_item");
				$(this).parentsUntil(".news").parent().children().not("h5").remove();
				$("#page-p-news .news").show();
				location.hash = "#/news/";
				return false;
			}
			else {
				fetch_news($(this).parentsUntil(".news").parent().attr("value"));
			}
		});
		$(this).attr("href", "#/news/{0}/".format($(this).parent().parent().attr("value")));
	});
}
function periodic() {
	counter += 0.5;
	counter_search += 0.5;
	current_pos += 0.5;
	apply_progress();
	if (counter >= 10.0) {
		update_periodic();
		counter = 0;
	}
	if (counter_search >= 120.0) {
		if ($("#page-p-search").length > 0) {
			search_submit(search_page, false);
			counter_search = 0;
		}
	}
}
function error_view(error_text, kind) {
	if (!kind) {
		kind = "danger";
	}
	html_error = '<div class="alert-message {1} fade in error-message"><a class="close" href="#">×</a><strong>{0}</strong></div>';
	$(".error-div > div > div").append(html_error.format(error_text, kind));
	$(".error-div").show();
	$(".alert-message .close").click(function () {
		$(this).parent().fadeOut(function () {$(this).remove();});
		if ($(".error-message").length == 0) {
			clear_error_view();
		}
	});
}
function clear_error_view() {
	$(".error-message").remove();
	$(".error-div").hide();
}
$(function () {
	update_periodic();
	setInterval(periodic, 500);
	$.ajax({
		url: "/relay/api.php",
		type: "GET",
		dataType: 'jsonp',
		data: "min_bitrate=128&active=1&not_full=1",
		success: function (resp) {
			var mp3index = -1;
			var oggindex = -1;
			var mp3ratio = 1;
			var oggratio = 1;
			sources = {};
			for(var i in resp) {
				var listeners = parseInt(resp[i]['listeners']);
				var limit = resp[i]['listener_limit'];
				if(limit == null)
					limit = 600;
				else
					limit = parseInt(limit);
				if(resp[i]['format'] == 'mp3' && (mp3index == -1 || listeners/limit < mp3ratio)) {
					mp3index = i;
					mp3ratio = listeners/limit;
				}
				if(resp[i]['format'] == 'ogg' && (oggindex == -1 || listeners/limit < oggratio)) {
					oggindex = i;
					oggratio = listeners/limit;
				}
			}
			if(oggindex != -1)
				sources['oga'] = "http://{0}.r-a-d.io:{1}{2}?_t={3}".format(resp[oggindex]['relay_name'], resp[oggindex]['port'], resp[oggindex]['mount'], Math.round(new Date().getTime()/1000.0));
			if(mp3index != -1)
				sources['mp3'] = "http://{0}.r-a-d.io:{1}{2}?_t={3}".format(resp[mp3index]['relay_name'], resp[mp3index]['port'], resp[mp3index]['mount'], Math.round(new Date().getTime()/1000.0));
			$("#player").jPlayer({
				ready: function () {
					$(this).jPlayer("setMedia", sources);
					$(".jp-play").attr("disabled", false);
				},
				supplied: Object.keys(sources).join(", "),
				//supplied: "oga, mp3",
				swfPath: window.swfpath,
				cssSelectorAncestor: "#streamconnect"
			});
			
			
		}
	});

	$("form .search").typeahead()
	//$("#testbox").typeahead()
	$("#search").submit(function () {
		return search_submit("1");
	});
	$(".topbar .container h3 > a").click(function () {
		$(".page").hide();
		clear_error_view();
		if($(".go .active") != $("#p-lastplayed")) {
			piwikTracker.setCustomUrl("/");
			piwikTracker.trackPageView("/index");
		}
		$("#page-p-home").slideDown();
		$(".topbar .nav li").removeClass("active");
		$("#p-home").addClass("active");
	});
	$("#expand-panel").click(function() {
		if($("#streamconnect-panel").css('display') == "none") { // show it!
			$("#streamconnect-panel").css('top', -($("#streamconnect-panel").height() + 12) + 'px');
			//$("#main-streamdata").css('top', -($("#streamconnect-panel").height() + 11) + 'px');
			$("#streamconnect-panel").css('display', 'inline');
			$("#streamconnect-panel").animate({
				top: 0,
				opacity: 1
			}, 600, function() {
				$("#streamconnect").css('border-radius', '0');
			});
		}
		else {
			var heightval = -($("#streamconnect-panel").height() + 12);
			$("#streamconnect").css('border-radius', '0 0 10px 10px');
			$("#streamconnect-panel").animate({
				top: heightval,
				opacity: 0
			}, 600, function() {
				
				$("#streamconnect-panel").css('display', 'none');
				//$("#main-streamdata").css('top', 0);
			});
		}
	});
	$(".go a").click(function() {
		if ($(this).parent().hasClass("active") != true) {
			$(".topbar .nav li").removeClass("active");
			$(this).parent().addClass("active");
			match = $("#page-{0}".format($(this).parent().attr("id")));
			if (match.length == 0) {
				get_page($(this).parent().attr("id"), false);
			}
			else {
				$(".page").hide();
				clear_error_view();
				var matchstr = $(this).parent().attr("id");
				matchstr = matchstr.substring(2, matchstr.length);
				var piwikurl = "/";
				if(matchstr != "home")
					piwikurl += matchstr;
				if(matchstr == "search")
					piwikurl += (search_query=="" ? "" : "/") + search_query;
				if(matchstr == "favorites")
					piwikurl += (fave_nick=="" ? "" : "/") + fave_nick;
				piwikTracker.setCustomUrl(piwikurl);
				piwikTracker.trackPageView(matchstr);
				match.slideDown();
			}
			switch($(this).parent().attr("id")) {
				case "p-home":
					hash = "#";
					break;
				case "p-news":
					hash = "#/news/";
					break;
				case "p-lastplayed":
					hash = "#/lastplayed/";
					break;
				case "p-queue":
					hash = "#/queue/";
					break;
				case "p-submit":
					hash = "#/submit/";
					break;
				case "p-staff":
					hash = "#/staff/";
					break;
				case "p-irc":
					hash = "#/IRC/";
					break;
				case "p-search":
					hash = "#/search/1/" + search_query;
					break;
				case "p-stats":
					hash = "#/stats/";
					break;
				case "p-favorites":
					hash = "#/favorites/" + fave_nick;
					break;
				default:
					hash = "#";
			}
			window.location.hash = hash;
		}
		return false;
	});
	$("#streamconnect .jp-play, #page-p-staff .media-grid a").twipsy({animate: true, placement: "below", trigger: "hover", fallback: "Default"});
	$("#panel-links a").twipsy({animate: true, placement: "right", trigger: "hover", fallback: "Default"});
	$("#page-p-home .djmedia").twipsy({animate: true, placement: "left", trigger: "hover", fallback: "Default"});
	hash = window.location.hash;
	target = "home";
	switch(hash) {
		case "#/queue/":
			target = "queue";
			break;
		case "#/submit/":
			target = "submit";
			break;
		case "#/staff/":
			target = "staff";
			break;
		case "#/IRC/":
			target = "irc";
			break;
		case "#/stats":
			target = "stats";
			break;
		default:
			re = hash.match("#/search/(\\d*)?/?(.*)?");
			target = "home";
			if (re) {
				target = "search";
				search_page = re[1] ? re[1] : "1";
				search_query = re[2] ? re[2] : "";
				$("#search input:text").first().val(search_query);
			}
			re = hash.match("#/news/(\\d*)?/?");
			if (re) {
				target = "news";
				nid = re[1];
			}
			re = hash.match("#/lastplayed/(sort|fave)?/?");
			if (re) {
				target = "lastplayed";
				lastplayed_order = "";
				if (re[1]) {
					lastplayed_order = re[1];
				}
			}
			re = hash.match("#/favorites/(.*)?");
			if (re) {
				target = "favorites";
				if(re[1] != undefined)
					fave_nick = re[1];
				else
					fave_nick = "";
			}
	}
	if(target == "home") {
		piwikTracker.setCustomUrl("/");
		piwikTracker.trackPageView("/index");
		redir = gup("x");
		if(redir == "redirect") {
			piwikTracker.setCustomVariable(1, "Redirected", "Yes", "visit");
		}
		else {
			piwikTracker.setCustomVariable(1, "Redirected", "No", "visit");
		}
	}
	else {
		piwikTracker.setCustomUrl("/" + target);
		piwikTracker.trackPageView(target);
	}
	match = $("#page-p-{0}".format(target));
	finish = false;
	if (match.length == 0) {
		switch (target) {
			case "search":
				url = "/search/search.php?query={0}&page={1}".format(search_query, search_page);
				finish = search_pagination;
				break;
			case "news":
				url = "/news/news.php";
				finish = function () {
					news_bindings();
					fetch_news(nid);
				}
				break;
			case "lastplayed":
				url = "/lastplayed/lp.php?page=1&sort={0}".format(lastplayed_order);
				finish = lastplayed_bind;
				break;
			case "favorites":
				if(fave_nick != "")
					url = "/favorites/favorites.php?nick={0}".format(fave_nick);
				else
					url = "/favorites/favorites.php";
				finish = faves_bind;
				break;
			default:
				url = false;
		}
		get_page("p-{0}".format(target), url, finish)
		$(".topbar .nav li").removeClass("active");
		$(".topbar .nav li#p-{0}".format(target)).addClass("active");
	}
	else {
		$(".page").hide();
		clear_error_view();
		match.slideDown();
	}
	fpnews_bindings();
	if (djmode == 14) {
		//setTimeout('addjvis()', 1000);
		$('#streamconnect .browplay-jp').first().after('<a class="fill btn info" onclick="runrave();" style="margin-top: 3px">ENABLE RAVE MODO</a>');
	}
});

function runscript(js)
{
	var t = document.createElement('script');
	t.setAttribute('type', 'text/javascript');
	t.setAttribute('src', js);
	document.getElementsByTagName('body')[0].appendChild(t);
}
function addjvis()
{
	runscript('/jvis/jvis.js');
}










/* USEFUL /ed/ITS
 * NEWS COMMENT-LINKAN
 */
function devify(lv)
{
	$('.cmt_text').each(
	function (index, para)
	{
		var o = $(para);
		o.html(o.html().replace(/&gt;&gt;([0-9]+)/g, '<a href="#" class="chanjumper">^^$1</a>'));
		var cj = o.children('.chanjumper').first();
		if (cj.length)
		{
			var id = cj.html().substr(2);
			o.parent().appendTo('#cmt'+id);
			//devify(lv+1);
			//return;
		}
	});
}
function charnage()
{
	var base = '.news>.comment';
	for (var a=0; a<10; a++)
	{
		base += '>.comment';
		$(base     ).css('background', a%2==0? '#fff':'#eee');
		$(base+'>*').css('background', a%2==0? '#fff':'#eee');
	}
}
function chanify()
{
	if (location.hash.indexOf('/dev') != -1 || enable_news_comments_nesting)
	{
		devify(1);
		//$('.chanjumper, .chanjumper+br').css('display','none');

		// SOMEONE PLEASE THINK UP A BETTER WAY TO DO THIS
		//$('.news>.comment>.comment').css('background','#ddd');
		//$('.news>.comment>.comment>*').css('background','#ddd');
		//$('.news>.comment>.comment>.comment').css('background','#fff');
		//$('.news>.comment>.comment>.comment>*').css('background','#fff');
		//$('.news>.comment>.comment>.comment>.comment').css('background','#ddd');
		//$('.news>.comment>.comment>.comment>.comment>*').css('background','#ddd');
		charnage(); // i cant believe ive done this

		$('.chanjumper').each(
		function (index, para)
		{
			var o = $(para);
			o.html(o.html().replace('^^','&gt;&gt;'));
		});
		return;
	}
	// hey, remember when I said I'd do a proper job for once?

	$('.cmt_text').each(
	function (index, para)
	{
		var o = $(para);
		o.html(o.html().replace(/&gt;&gt;([0-9]+)/g, '<a href="#" class="chanjumper">\&gt;\&gt;$1</a>'));
	});

	// yeah well I lied

	$('.chanjumper').each(
	function (index, para)
	{
		var o = $(para);
		o.click(function(e) {
			e.preventDefault();
			$('.comment').each(
			function (index, para)
			{
				// WE NEED TO GO DEEPER
				$(this).css('border-left','none');
			});
			var id = $(this).html().substr(8);
			$('#cmt'+id).css('border-left','8px solid #90f');
			$('html,body').animate({scrollTop:
				$('#cmt'+id).offset().top}, 500);
		});
	});
}
function chanjump()
{
	alert(this.innerHTML);
}










/*
 * USELESS /ed/ITS
 * PACMEN AND UNTZMODE
 */
var loadgif = '/css/load.gif';
function lastplayed_page_inc(n)
{
	lastplayed_page += n;
	if (lastplayed_page < 1) lastplayed_page = 1;
	fetch_lastplayed(lastplayed_page, lastplayed_order);
	$('#paginpn').html('<img src="'+loadgif+'" />');
	$('#paginnn').html('<img src="'+loadgif+'" />');
}
var pacpos = [];
var pacobj = [];
function pacrun(n)
{
	if (pacobj.length <= n)
	{
		pacpos[n] = -10;
		pacobj[n] = document.createElement('img');
		pacobj[n].setAttribute('src', loadgif);
		pacobj[n].style.position = 'absolute';
		pacobj[n].style.left = 0;
		pacobj[n].style.bottom = 0;
		document.getElementsByTagName('html')[0].appendChild(pacobj[n]);
		pacmov(n);
		pacobj[n].onclick = function()
		{
			var m = pacpos.length * 2;
			for (n = pacpos.length; n < m; n++)
			{
				pacrun(n);
			}
			for (n = 0; n < pacpos.length; n++)
			{
				pacpos[n] = Math.random() * 100;
				pacobj[n].style.bottom = Math.random() * 100 + '%';
			}
		};
	}
}
function pacmov(i)
{
	if (i != 0) return;
	for (var n=0; n<pacpos.length; n++)
	{
		pacpos[n] += 0.1;
		if (pacpos[n] > 100) pacpos[n] = -5;
		pacobj[n].style.left = pacpos[n] + '%';
	}
	setTimeout('pacmov(0)',70);
}

var raveC = 0;
var rave1 = null;
var rave2 = null;
var rave3 = null;
var rave4 = null;
var party = null;
var parto = 0;
function runrave()
{
	if(party != null) {
		document.title = 'R/a/dio';
		$("#logo-image-div").css('background-image', 'url("/res/img/logo_image_small.png")');
		party.remove();
		rave1.css('box-shadow', '0');
		rave2.css('box-shadow', '0');
		rave3.css('background', '');
		
		$('#streamconnect .browplay-jp').next().text('ENABLE RAVE MODO')
		
		rave1 = null;
		rave2 = null;
		rave3 = null;
		rave4 = null;
		party = null;
		return;
	}
	document.title = 'R/a/ve';
	$("#logo-image-div").css('background-image', 'url("/res/img/logo_rave.gif")');
	//document.getElementsByTagName('body')[0].style.height = '100%';
	rave1 = $('.content-top').first();
	rave2 = $('.content-top+.row').first();
	rave3 = $('.border').slice(1).first();
	rave4 = $('body').first();

	$('body').first().append('<div id="party"><div>PARTY HARD</div><div>PARTY HARD</div></div>');
	$('#party')
		.css('position', 'absolute')
		.css('font-weight', 'bold')
		.css('font-size', '5em')
		.css('width', '98%')
		.css('left', '1%')
		.css('top', '0');
	$('#party div')
		.css('width', '100%')
		.css('color', 'inherit');
	$('#party div').first().css('text-align', 'left');
	$('#party div').last().css('text-align', 'right');
	$('#streamconnect .browplay-jp').next().text('RAVE MODO OFF')
	$('html').css('height','100%');
	$('body').css('height','100%');
	party = $('#party').first();
	rave();
	raveb();
}
function rave()
{
	if(party == null)
		return;
	var rc1 = raveC;
	var rc2 = raveC + 10;
	var rc3 = raveC + 20;
	var rc4 = raveC + 30;
	if (rc2 > 360) rc2 -= 360;
	if (rc3 > 360) rc3 -= 360;
	if (rc4 > 360) rc4 -= 360;
	raveC += 50;
	if (raveC > 360) raveC -= 360;
	rave1.css('box-shadow', '0 1px 16px hsl(' + rc1 + ',100%,50%)');
	rave2.css('box-shadow', '0 0 32px hsl(' + rc2 + ',100%,50%)');
	//rave3.css('box-shadow', '0 0 64px hsl(' + rc3 + ',100%,50%)');
	rave4.css('background', 'hsla(' + rc4 + ',100%,50%,0.3)');
	setTimeout('rave()', 100);
}
function raveb()
{
	if(party == null)
		return;
	parto += 0.06;
	if (parto > 1) parto = 0;
	var rc2 = raveC + 30;
	if (rc2 > 360) rc2 -= 360;
	var f = Math.sin(Math.PI*2*parto) * 0.5 + 0.5;
	f = (100 * 0.6 * f) + 100 * 0.2;
	party
		.css('top', f+'%')
		.css('color', 'hsl(' + rc2 + ',100%,50%)');
	setTimeout('raveb()', 10);
}
