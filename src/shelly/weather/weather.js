// weather_v0_9_0 G2 weather runtime for P0015.
var SCRIPT_NAME = "weather_v0_9_0";

var LAT = "59.6214405";
var LON = "17.7336153";
var KEY_WEATHER_ACT = "g2.weather.act";
var SOLAR_GAIN_FACTOR_KWH_PER_MJ = 2.0;

var DAILY_VARS = "shortwave_radiation_sum,temperature_2m_mean,relative_humidity_2m_mean";
var HOURLY_VARS = "temperature_2m";
var API_BASE = "https://api.open-meteo.com/v1/forecast";

function log(s) {
  print(SCRIPT_NAME + " " + String(s || ""));
}

function clip(v, lo, hi) {
  v = Number(v);
  if (v !== v) return lo;
  if (v < lo) return lo;
  if (v > hi) return hi;
  return v;
}

function round1(v) {
  return Math.round(Number(v) * 10) / 10;
}

function toNumber(v, fallback) {
  var n = Number(v);
  return n === n ? n : fallback;
}

function pad2(n) {
  n = Number(n);
  return n < 10 ? "0" + n : String(n);
}

function todayString() {
  var d = new Date();
  return d.getFullYear() + "-" + pad2(d.getMonth() + 1) + "-" + pad2(d.getDate());
}

function buildDailyUrl(day) {
  return API_BASE +
    "?latitude=" + LAT +
    "&longitude=" + LON +
    "&daily=" + DAILY_VARS +
    "&start_date=" + day +
    "&end_date=" + day +
    "&timezone=auto";
}

function buildHourlyUrl() {
  return API_BASE +
    "?latitude=" + LAT +
    "&longitude=" + LON +
    "&hourly=" + HOURLY_VARS +
    "&forecast_hours=1" +
    "&timezone=auto";
}

function parseDailyWeather(body) {
  var js;
  var daily;
  var swr;
  var tavg;
  var hum;

  try {
    js = JSON.parse(body);
  } catch (e) {
    log("JSON DAILY ERR");
    return { solar_kwh_today: 0, temp_avg_today: 0, humidity_avg_today: 0 };
  }

  daily = js && js.daily;
  if (!daily || typeof daily !== "object") {
    log("NO DAILY");
    return { solar_kwh_today: 0, temp_avg_today: 0, humidity_avg_today: 0 };
  }

  swr = daily.shortwave_radiation_sum && daily.shortwave_radiation_sum.length ? toNumber(daily.shortwave_radiation_sum[0], 0) : 0;
  if (swr < 0) swr = 0;
  tavg = daily.temperature_2m_mean && daily.temperature_2m_mean.length ? toNumber(daily.temperature_2m_mean[0], 0) : 0;
  hum = daily.relative_humidity_2m_mean && daily.relative_humidity_2m_mean.length ? toNumber(daily.relative_humidity_2m_mean[0], 0) : 0;

  return {
    solar_kwh_today: Math.round(clip(swr * SOLAR_GAIN_FACTOR_KWH_PER_MJ, 0, 999)),
    temp_avg_today: round1(clip(tavg, -99.9, 99.9)),
    humidity_avg_today: round1(clip(hum, 0, 100))
  };
}

function parseHourlyWeather(body) {
  var js;
  var hourly;
  var temp;

  try {
    js = JSON.parse(body);
  } catch (e) {
    log("JSON HOURLY ERR");
    return { temp_now: 0 };
  }

  hourly = js && js.hourly;
  if (!hourly || typeof hourly !== "object") {
    log("NO HOURLY");
    return { temp_now: 0 };
  }

  temp = hourly.temperature_2m && hourly.temperature_2m.length ? toNumber(hourly.temperature_2m[0], 0) : 0;
  return { temp_now: round1(clip(temp, -99.9, 99.9)) };
}

function httpGet(url, cb) {
  Shelly.call("HTTP.GET", { url: url, timeout: 15 }, function (res, err) {
    if (err || !res || !res.body) {
      log("HTTP ERR");
      cb(null);
      return;
    }
    cb(String(res.body || ""));
  });
}

function kvsSet(key, value, cb) {
  Shelly.call("KVS.Set", { key: key, value: value }, function (res, err) {
    if (err) {
      log("KVS ERR");
      cb(false);
      return;
    }
    log("KVS OK");
    cb(true);
  });
}

function selfStop() {
  Shelly.call("Script.List", {}, function (res) {
    var scripts = res && res.scripts;
    var i;
    if (!scripts) return;
    for (i = 0; i < scripts.length; i++) {
      if (scripts[i] && scripts[i].name === SCRIPT_NAME) {
        Shelly.call("Script.Stop", { id: scripts[i].id });
        return;
      }
    }
  });
}

function runWeather() {
  var day = todayString();
  var dailyUrl = buildDailyUrl(day);
  var hourlyUrl = buildHourlyUrl();
  var act = { solar_kwh_today: 0, temp_now: 0, temp_avg_today: 0, humidity_avg_today: 0 };
  var daily;
  var hourly;

  log("BOT");
  log("DATE " + day);
  log("DAILY GET");
  httpGet(dailyUrl, function (dailyBody) {
    if (dailyBody) {
      log("DAILY OK len=" + dailyBody.length);
      daily = parseDailyWeather(dailyBody);
      act.solar_kwh_today = daily.solar_kwh_today;
      act.temp_avg_today = daily.temp_avg_today;
      act.humidity_avg_today = daily.humidity_avg_today;
    }

    log("HOURLY GET");
    httpGet(hourlyUrl, function (hourlyBody) {
      if (hourlyBody) {
        log("HOURLY OK len=" + hourlyBody.length);
        hourly = parseHourlyWeather(hourlyBody);
        act.temp_now = hourly.temp_now;
      }

      log("KVS SET solar=" + act.solar_kwh_today +
        " temp=" + act.temp_now +
        " avg=" + act.temp_avg_today +
        " hum=" + act.humidity_avg_today);
      kvsSet(KEY_WEATHER_ACT, act, function () {
        log("DONE");
        selfStop();
      });
    });
  });
}

runWeather();
