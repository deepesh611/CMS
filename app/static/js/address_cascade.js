/**
 * Address cascade for India + GCC / Middle East.
 *
 * Forward:  country → state → (district) → city → locality → suburb
 * Reverse:  country + postal code → auto-fills the rest
 *
 * Postal code: free-text (#address_pincode) + dropdown (#address_pincode_picker).
 * Typing a known code syncs the dropdown and fills address fields.
 */
(function () {
  var DATA_URL = "/static/data/geo_data.json";

  var countryEl = document.getElementById("address_country");
  var stateEl = document.getElementById("address_state");
  var districtEl = document.getElementById("address_district");
  var cityEl = document.getElementById("address_city");
  var localityEl = document.getElementById("address_locality");
  var suburbEl = document.getElementById("address_suburb");
  var pincodeEl = document.getElementById("address_pincode");
  var pickerEl = document.getElementById("address_pincode_picker");
  var districtWrapper = document.getElementById("district-wrapper");

  if (!countryEl || !stateEl || !cityEl || !pincodeEl) return;

  var geo = null;
  var preset = window.__addressPreset || {};
  var applying = false;
  var inputTimer = null;
  /** Full postal list for the current country/state/city scope (unfiltered). */
  var pickerBaseEntries = [];
  /** Country-wide list used for live typeahead suggestions. */
  var countryPostalEntries = [];

  function clearSelect(el, placeholder) {
    if (!el) return;
    el.innerHTML = "";
    var opt = document.createElement("option");
    opt.value = "";
    opt.textContent = placeholder;
    el.appendChild(opt);
  }

  function fillSelect(el, items, placeholder, selected) {
    clearSelect(el, placeholder);
    if (!el || !items) return;
    items.forEach(function (name) {
      var opt = document.createElement("option");
      opt.value = name;
      opt.textContent = name;
      if (selected && selected === name) opt.selected = true;
      el.appendChild(opt);
    });
  }

  function usesDistricts(country) {
    return geo && geo.has_districts && geo.has_districts.indexOf(country) !== -1;
  }

  function setDistrictVisible(show) {
    if (!districtWrapper) return;
    districtWrapper.style.display = show ? "" : "none";
    if (!show && districtEl) clearSelect(districtEl, "— Select District —");
  }

  function cityKeyPrefix() {
    var country = countryEl.value;
    var state = stateEl.value;
    if (!country || !state) return null;
    if (usesDistricts(country)) {
      var district = districtEl ? districtEl.value : "";
      if (!district) return null;
      return country + "|" + state + "|" + district;
    }
    return country + "|" + state;
  }

  function localitiesFor(city) {
    var prefix = cityKeyPrefix();
    if (prefix && city && geo.localities) {
      var key = prefix + "|" + city;
      var real = geo.localities[key];
      if (real && real.length) return real.slice();
    }
    // Fallback only when dataset has no localities for this city
    var suffixes = ["Central", "North", "South", "East", "West"];
    return suffixes.map(function (s) { return city + " " + s; });
  }

  function suburbsFor(city, locality) {
    var prefix = cityKeyPrefix();
    if (prefix && city && locality && geo.suburbs) {
      var key = prefix + "|" + city + "|" + locality;
      var real = geo.suburbs[key];
      if (real && real.length) return real.slice();
    }
    var suffixes = ["Block A", "Block B", "Phase 1", "Phase 2", "Extension"];
    return suffixes.map(function (s) { return locality + " — " + s; });
  }

  var SUGGEST_LIMIT = 80;
  var INDIA_MIN_CHARS = 2;
  var postalSizeCache = {};

  function entryLabel(e) {
    return (e.area || "") + " — " + e.code;
  }

  function sortPostalEntries(entries) {
    return entries.slice().sort(function (a, b) {
      var la = entryLabel(a).toLowerCase();
      var lb = entryLabel(b).toLowerCase();
      if (la < lb) return -1;
      if (la > lb) return 1;
      return 0;
    });
  }

  function postalIndexSizeHint(country) {
    if (postalSizeCache[country] != null) return postalSizeCache[country];
    var index = (geo.postal_index && geo.postal_index[country]) || {};
    var n = 0;
    for (var k in index) {
      if (!Object.prototype.hasOwnProperty.call(index, k)) continue;
      n++;
      if (n > SUGGEST_LIMIT) break;
    }
    postalSizeCache[country] = n;
    return n;
  }

  function isLargePostalIndex(country) {
    return postalIndexSizeHint(country) > SUGGEST_LIMIT;
  }

  /**
   * Fast postal search — never expands the full India index into DOM.
   * Matches code prefix; optional state/district/city filters.
   */
  function searchPostal(country, query, filters, limit) {
    filters = filters || {};
    limit = limit || SUGGEST_LIMIT;
    var index = (geo.postal_index && geo.postal_index[country]) || {};
    var q = String(query || "").trim();
    var qLower = q.toLowerCase();
    var qCompact = q.replace(/[\s-]/g, "").toLowerCase();
    var out = [];
    var large = isLargePostalIndex(country);

    // India (~19k PINs): require typing before any scan / DOM work
    if (large && qCompact.length < INDIA_MIN_CHARS) {
      return out;
    }

    // Direct O(1) path when query is an exact known code
    if (qCompact && (index[q] || index[qCompact])) {
      var exactCode = index[q] ? q : qCompact;
      var exactHits = index[exactCode];
      for (var eh = 0; eh < exactHits.length && out.length < limit; eh++) {
        var ehit = exactHits[eh];
        if (filters.state && ehit[0] !== filters.state) continue;
        if (filters.district && (ehit[1] || "") !== filters.district) continue;
        if (filters.city && ehit[2] !== filters.city) continue;
        out.push({
          code: exactCode,
          area: ehit[3] || ehit[2],
          state: ehit[0],
          district: ehit[1] || "",
          city: ehit[2]
        });
      }
      if (out.length) return sortPostalEntries(out);
    }

    for (var code in index) {
      if (!Object.prototype.hasOwnProperty.call(index, code)) continue;
      if (out.length >= limit) break;

      var codeCompact = String(code).replace(/[\s-]/g, "").toLowerCase();
      var codeMatch =
        !qCompact ||
        codeCompact.indexOf(qCompact) === 0 ||
        String(code).toLowerCase().indexOf(qLower) === 0;

      var hits = index[code];
      for (var h = 0; h < hits.length && out.length < limit; h++) {
        var hit = hits[h];
        var state = hit[0];
        var district = hit[1] || "";
        var city = hit[2];
        var area = hit[3] || city;
        if (filters.state && state !== filters.state) continue;
        if (filters.district && district !== filters.district) continue;
        if (filters.city && city !== filters.city) continue;

        var areaMatch =
          qCompact &&
          /[a-z]/i.test(q) &&
          String(area).toLowerCase().indexOf(qLower) !== -1;

        if (!codeMatch && !areaMatch) continue;

        out.push({
          code: code,
          area: area,
          state: state,
          district: district,
          city: city
        });
      }
    }
    return sortPostalEntries(out);
  }

  function postalEntries(country, filterState, filterDistrict, filterCity) {
    return searchPostal(
      country,
      "",
      {
        state: filterState || "",
        district: filterDistrict || "",
        city: filterCity || ""
      },
      SUGGEST_LIMIT
    );
  }

  function resolvePostal(country, raw) {
    if (!country || !geo || !geo.postal_index) return null;
    var index = geo.postal_index[country] || {};
    var code = String(raw || "").trim();
    if (!code) return null;
    if (index[code]) return { code: code, hits: index[code] };

    var cleaned = code.replace(/[\s-]/g, "");
    if (cleaned !== code && index[cleaned]) {
      return { code: cleaned, hits: index[cleaned] };
    }

    if (country === "India" && /^\d+$/.test(cleaned)) {
      if (cleaned.length === 6 && index[cleaned]) {
        return { code: cleaned, hits: index[cleaned] };
      }
      if (cleaned.length > 0 && cleaned.length < 6) {
        var padded = ("000000" + cleaned).slice(-6);
        if (index[padded]) return { code: padded, hits: index[padded] };
      }
      return null;
    }

    var lower = cleaned.toLowerCase();
    if (cleaned.length >= 2) {
      var keys = Object.keys(index);
      for (var j = 0; j < keys.length; j++) {
        var k2 = keys[j];
        if (k2.toLowerCase() === lower) return { code: k2, hits: index[k2] };
        if (k2.replace(/[\s-]/g, "").toLowerCase() === lower) {
          return { code: k2, hits: index[k2] };
        }
      }
    }
    return null;
  }

  function renderPickerOptions(entries, selectedCode, placeholderText) {
    if (!pickerEl) return;
    var placeholder =
      placeholderText ||
      (entries.length === 0
        ? "— Type to search postal codes —"
        : "— Or pick from list (" + entries.length + ") —");
    clearSelect(pickerEl, placeholder);
    var frag = document.createDocumentFragment();
    for (var i = 0; i < entries.length; i++) {
      var e = entries[i];
      var opt = document.createElement("option");
      opt.value = e.code;
      opt.textContent = entryLabel(e);
      opt.dataset.state = e.state;
      opt.dataset.district = e.district || "";
      opt.dataset.city = e.city;
      opt.dataset.area = e.area;
      if (selectedCode && selectedCode === e.code) opt.selected = true;
      frag.appendChild(opt);
    }
    pickerEl.appendChild(frag);
  }

  function setPincodePicker(entries, selectedCode, placeholderText) {
    pickerBaseEntries = (entries || []).slice(0, SUGGEST_LIMIT);
    renderPickerOptions(pickerBaseEntries, selectedCode || "", placeholderText);
  }

  function resetPostalPicker(country) {
    countryPostalEntries = [];
    pickerBaseEntries = [];
    var n = country ? postalIndexSizeHint(country) : 0;
    if (country && n > 0 && n <= SUGGEST_LIMIT) {
      setPincodePicker(searchPostal(country, "", {}, SUGGEST_LIMIT), "");
    } else {
      setPincodePicker(
        [],
        "",
        country === "India"
          ? "— Type at least " + INDIA_MIN_CHARS + " PIN digits —"
          : "— Type to search postal codes —"
      );
    }
  }

  function filterPincodeSuggestions(query, selectedCode) {
    var country = countryEl.value;
    if (!country) {
      setPincodePicker([], "");
      return [];
    }
    var filters = {};
    if (stateEl.value) filters.state = stateEl.value;
    if (usesDistricts(country) && districtEl && districtEl.value) {
      filters.district = districtEl.value;
    }
    if (cityEl.value) filters.city = cityEl.value;

    var filtered = searchPostal(country, query, filters, SUGGEST_LIMIT);
    var placeholder =
      !String(query || "").trim() && country === "India"
        ? "— Type at least " + INDIA_MIN_CHARS + " PIN digits —"
        : filtered.length
          ? null
          : "— No matches —";
    renderPickerOptions(filtered, selectedCode || "", placeholder);
    return filtered;
  }

  function syncPickerToCode(country, code, hit) {
    if (!pickerEl || !code) return;
    for (var i = 0; i < pickerEl.options.length; i++) {
      if (pickerEl.options[i].value === code) {
        pickerEl.selectedIndex = i;
        return;
      }
    }
    var entry = {
      code: code,
      area: hit ? hit[3] || hit[2] : code,
      state: hit ? hit[0] : "",
      district: hit ? hit[1] || "" : "",
      city: hit ? hit[2] : ""
    };
    var extras = searchPostal(
      country,
      code,
      { state: entry.state, district: entry.district, city: entry.city },
      SUGGEST_LIMIT
    );
    if (!extras.some(function (e) { return e.code === code; })) {
      extras.unshift(entry);
    }
    setPincodePicker(extras, code);
  }

  function onCountryChange(opts) {
    opts = opts || {};
    var country = countryEl.value;
    var states = (geo.states && geo.states[country]) || [];
    fillSelect(stateEl, states, "— Select State —", opts.state || "");
    setDistrictVisible(usesDistricts(country));
    clearSelect(districtEl, "— Select District —");
    clearSelect(cityEl, "— Select City —");
    clearSelect(localityEl, "— Select Locality —");
    clearSelect(suburbEl, "— Select Suburb —");

    if (opts.pincode) {
      pincodeEl.value = opts.pincode;
    } else if (!opts.state) {
      pincodeEl.value = "";
    }

    resetPostalPicker(country);
    if (opts.pincode) {
      applyPostalCode(opts.pincode, { silentText: true });
    } else if (opts.state) {
      onStateChange(opts);
    }
  }

  function onStateChange(opts) {
    opts = opts || {};
    if (applying) return;
    var country = countryEl.value;
    var state = stateEl.value;
    clearSelect(cityEl, "— Select City —");
    clearSelect(localityEl, "— Select Locality —");
    clearSelect(suburbEl, "— Select Suburb —");

    if (!country || !state) {
      resetPostalPicker(country);
      return;
    }

    if (usesDistricts(country)) {
      var districts = (geo.districts && geo.districts[country + "|" + state]) || [];
      fillSelect(districtEl, districts, "— Select District —", opts.district || "");
      setDistrictVisible(true);
      // Don't preload thousands of state PINs — wait for typing or city
      resetPostalPicker(country);
      if (opts.district) onDistrictChange(opts);
    } else {
      setDistrictVisible(false);
      var cities = (geo.cities && geo.cities[country + "|" + state]) || [];
      fillSelect(cityEl, cities, "— Select City —", opts.city || "");
      setPincodePicker(postalEntries(country, state), "");
      if (opts.city) onCityChange(opts);
    }
  }

  function onDistrictChange(opts) {
    opts = opts || {};
    if (applying) return;
    var country = countryEl.value;
    var state = stateEl.value;
    var district = districtEl ? districtEl.value : "";
    clearSelect(localityEl, "— Select Locality —");
    clearSelect(suburbEl, "— Select Suburb —");
    if (!country || !state || !district) {
      clearSelect(cityEl, "— Select City —");
      resetPostalPicker(country);
      return;
    }
    var key = country + "|" + state + "|" + district;
    var cities = (geo.cities && geo.cities[key]) || [];
    fillSelect(cityEl, cities, "— Select City —", opts.city || "");
    // City-scoped list is usually small enough; still capped by SUGGEST_LIMIT
    setPincodePicker(postalEntries(country, state, district), "");
    if (opts.city) onCityChange(opts);
  }

  function onCityChange(opts) {
    opts = opts || {};
    if (applying) return;
    var city = cityEl.value;
    clearSelect(suburbEl, "— Select Suburb —");
    if (!city) {
      clearSelect(localityEl, "— Select Locality —");
      return;
    }
    var locs = localitiesFor(city);
    fillSelect(localityEl, locs, "— Select Locality —", opts.locality || locs[0] || "");
    var country = countryEl.value;
    var state = stateEl.value;
    var district = usesDistricts(country) ? (districtEl.value || "") : "";
    setPincodePicker(
      postalEntries(country, state, district || null, city),
      ""
    );
    // Keep typed/canonical code selected in picker if it still applies
    var resolved = resolvePostal(country, pincodeEl.value);
    if (resolved) syncPickerToCode(country, resolved.code, resolved.hits[0]);
    onLocalityChange(opts);
  }

  function onLocalityChange(opts) {
    opts = opts || {};
    if (applying) return;
    var city = cityEl.value;
    var locality = localityEl ? localityEl.value : "";
    if (!locality) {
      clearSelect(suburbEl, "— Select Suburb —");
      return;
    }
    var subs = suburbsFor(city, locality);
    fillSelect(suburbEl, subs, "— Select Suburb —", opts.suburb || subs[0] || "");
  }

  /**
   * Reverse-fill from postal code.
   * opts.fromPicker — use selected option's dataset path
   * opts.silentText — don't rewrite the text field (preset load)
   */
  function applyPostalCode(raw, opts) {
    opts = opts || {};
    if (applying) return;

    var country = countryEl.value;
    if (!country) return;

    var resolved = resolvePostal(country, raw);
    if (!resolved) {
      // No match — leave text as typed, reset picker selection
      if (pickerEl) pickerEl.selectedIndex = 0;
      return;
    }

    var code = resolved.code;
    var hits = resolved.hits;
    var state = hits[0][0];
    var district = hits[0][1] || "";
    var city = hits[0][2];

    if (opts.fromPicker && pickerEl && pickerEl.selectedIndex > 0) {
      var selected = pickerEl.options[pickerEl.selectedIndex];
      if (selected && selected.value === code) {
        state = selected.dataset.state || state;
        district = selected.dataset.district || district;
        city = selected.dataset.city || city;
      }
    }

    applying = true;
    try {
      if (!opts.silentText) {
        pincodeEl.value = code; // canonical form (e.g. padded PIN)
      } else {
        pincodeEl.value = code;
      }

      fillSelect(
        stateEl,
        (geo.states && geo.states[country]) || [],
        "— Select State —",
        state
      );

      if (usesDistricts(country)) {
        setDistrictVisible(true);
        var districts = (geo.districts && geo.districts[country + "|" + state]) || [];
        fillSelect(districtEl, districts, "— Select District —", district);
        var cities = (geo.cities && geo.cities[country + "|" + state + "|" + district]) || [];
        fillSelect(cityEl, cities, "— Select City —", city);
      } else {
        setDistrictVisible(false);
        var cities2 = (geo.cities && geo.cities[country + "|" + state]) || [];
        fillSelect(cityEl, cities2, "— Select City —", city);
      }

      var locs = localitiesFor(city);
      var areaName = hits[0][3] || "";
      var locality =
        opts.locality && locs.indexOf(opts.locality) >= 0
          ? opts.locality
          : preset.locality && locs.indexOf(preset.locality) >= 0
            ? preset.locality
            : locs.indexOf(areaName) >= 0
              ? areaName
              : locs[0];
      fillSelect(localityEl, locs, "— Select Locality —", locality);

      var subs = suburbsFor(city, locality);
      var suburb =
        opts.suburb && subs.indexOf(opts.suburb) >= 0
          ? opts.suburb
          : areaName && subs.indexOf(areaName) >= 0
            ? areaName
            : preset.suburb && subs.indexOf(preset.suburb) >= 0
              ? preset.suburb
              : subs[0];
      fillSelect(suburbEl, subs, "— Select Suburb —", suburb);

      // Dropdown: show codes for this city, select the matched one
      setPincodePicker(
        postalEntries(
          country,
          state,
          usesDistricts(country) ? district : null,
          city
        ),
        code
      );
      syncPickerToCode(country, code, hits[0]);
    } finally {
      applying = false;
    }
  }

  function onPickerChange() {
    if (!pickerEl || !pickerEl.value) return;
    applyPostalCode(pickerEl.value, { fromPicker: true });
  }

  function onPincodeTextCommit() {
    applyPostalCode(pincodeEl.value, {});
  }

  /**
   * Every keystroke: narrow dropdown suggestions immediately.
   * When the typed value fully resolves to a known code, autofill address.
   */
  function onPincodeInput() {
    var raw = pincodeEl.value;
    var country = countryEl.value;

    // Live suggestion search (prefix against index — no giant prebuild)
    filterPincodeSuggestions(raw, "");

    clearTimeout(inputTimer);
    inputTimer = setTimeout(function () {
      if (!country) return;
      var resolved = resolvePostal(country, raw);
      if (resolved) {
        applyPostalCode(resolved.code, {});
      }
    }, 150);
  }

  function bind() {
    countryEl.addEventListener("change", function () {
      onCountryChange();
    });
    stateEl.addEventListener("change", function () {
      onStateChange();
    });
    if (districtEl) {
      districtEl.addEventListener("change", function () {
        onDistrictChange();
      });
    }
    cityEl.addEventListener("change", function () {
      onCityChange();
    });
    if (localityEl) {
      localityEl.addEventListener("change", function () {
        onLocalityChange();
      });
    }
    if (pickerEl) {
      pickerEl.addEventListener("change", onPickerChange);
    }
    pincodeEl.addEventListener("input", onPincodeInput);
    pincodeEl.addEventListener("change", onPincodeTextCommit);
    pincodeEl.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        onPincodeTextCommit();
      }
    });
    pincodeEl.addEventListener("blur", onPincodeTextCommit);
  }

  function initWithData(data) {
    geo = data;
    fillSelect(
      countryEl,
      geo.countries || [],
      "— Select Country —",
      preset.country || ""
    );
    clearSelect(stateEl, "— Select State —");
    clearSelect(districtEl, "— Select District —");
    clearSelect(cityEl, "— Select City —");
    clearSelect(localityEl, "— Select Locality —");
    clearSelect(suburbEl, "— Select Suburb —");
    if (pickerEl) clearSelect(pickerEl, "— Or pick from list —");
    if (preset.pincode) pincodeEl.value = preset.pincode;
    setDistrictVisible(false);
    bind();

    if (preset.country) {
      onCountryChange({
        state: preset.state,
        district: preset.district,
        city: preset.city,
        locality: preset.locality,
        suburb: preset.suburb,
        pincode: preset.pincode
      });
    }
  }

  fetch(DATA_URL)
    .then(function (res) {
      if (!res.ok) throw new Error("Failed to load geo data (" + res.status + ")");
      return res.json();
    })
    .then(initWithData)
    .catch(function (err) {
      console.error("address_cascade:", err);
    });
})();
