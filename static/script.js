/* jshint strict: true */
/* jshint jquery: true */
/* jshint -W100 */

function daftar(s) {
    "use strict";
    switch (s) {
    case '1':
        return 'نخست';
    case '2':
        return 'دوم';
    case '3':
        return 'سوم';
    case '4':
        return 'چهارم';
    case '5':
        return 'پنجم';
    case '6':
        return 'ششم';
    case '7':
        return 'هفتم';
    case '8':
        return 'هشتم';
    case '9':
        return 'نهم';
    case '10':
        return 'دهم';
    case '11':
        return 'یازدهم';
    case '12':
        return 'دوازدهم';
    case '13':
        return 'سیزدهم';
    case '14':
        return 'چهاردهم';
    case '15':
        return 'پانزدهم';
    }
}

function num2fa(string) {
    "use strict";
    var newstring = '';
    $(string.split('')).each(function () {
        newstring += String.fromCharCode(this.charCodeAt(0) + 1728);
    });
    return newstring;
}

function copy_citation(text) {
    "use strict";
    window.prompt("برای یادکرد در ویکی‌پدیا رونوشت بردارید:", text);
}

function nonum_mosavab(mosavab) {
    "use strict";
    if (!/\d\d$/.test(mosavab) && !/ \d$/.test(mosavab)) {
        return mosavab.replace(/\d$/, '');
    }
    return mosavab;
}

function nonum_motaradef(motaradef) {
    "use strict";
    if (!/\d\d$/.test(motaradef)) {
        return motaradef.replace(/ \d$/, '').replace(/ \d،/, '،');
    }
    return motaradef;
}

function nonum_biganeh(biganeh) {
    "use strict";
    return biganeh.replace(/^\d /, '').replace(/( \d)+(?=, | \(| ?\/ |$)/g, '');
}

function citation2string(citation) {
    // get citation object and return citation string
    "use strict";
    var string = '<ref>{{یادکرد فرهنگستان';
    string += ' | مصوب=' + citation.mosavab;
    string += ' | بیگانه=' + citation.biganeh;
    if (citation.biganeh) {
        string += ' | بیگانه در فارسی=';
    }
    if (citation.mosavab_motaradef) {
        string += ' | مصوب مترادف=' + citation.mosavab_motaradef;
    }
    if (citation.biganeh_motaradef) {
        string += ' | بیگانهٔ مترادف=' + citation.biganeh_motaradef;
    }
    if (citation.biganeh_motaradef) {
        string += ' | بیگانه در فارسی مترادف=';
    }
    string += ' | حوزه=' + citation.hozeh;
    string += ' | دفتر=' + citation.daftar;
    string += ' | بخش=فارسی';
    string += ' | سرواژه=' + citation.sarvazheh;
    string += '}}</ref>';
    return  string;
}

function mosavab_motaradef(lines, start_line) {
    "use strict";
    var firsttime = true;
    var line, mm;
    for (var i=start_line; i < lines.length; i++) {
        line = lines[i].trim();
        line = nonum_motaradef(line);
        if (!line) continue;
        // [\u0600-\u06FF] is the Arabic (Unicode block)
        // https://en.wikipedia.org/wiki/Arabic_%28Unicode_block%29
        line = /[\u0600-\u06FF \u200c]+([\w] )?/.exec(line);
        if (!line) continue;
        line = line[0].trim();
        if (!line) continue;
        if (firsttime) {
            mm = nonum_motaradef(line);
            firsttime = false;
        } else {
            mm += '، ' + nonum_motaradef(line);
        }
    }
    return mm;
}

function biganeh_motaradef(lines, start_line) {
    "use strict";
    var firsttime = true;
    var line, bm;
    for (var i=start_line; i < lines.length; i++) {
        line = lines[i].trim();
        if (!line) continue;
        line = /\w[ \w-,]{2,}(?=$|[\u0600-\u06FF\u200c])/g.exec(line);
        if (!line) continue;
        line = line[0].trim();
        if (!line) continue;
        if (firsttime) {
            bm = nonum_biganeh(line);
            firsttime = false;
        } else {
            bm += ', ' + nonum_biganeh(line);
        }
    }
    return bm;
}

function parse_tarif(tarif, citation) {
    "use strict";
    if (tarif.indexOf('متـ . ') !== -1) {
        //tarif has at list one synonym
        var postmot = tarif.split('متـ . ')[1];
        if (postmot.indexOf('*') !== -1) {
            // the star indicates some kind of comment.
            // e.g. واژه * مصوب فرهنگستان اول
            // also see سرگذشت خود
            postmot = postmot.split('*')[0].trim();
        }
        // may contain newline. see واکنشگاه هسته‌ای
        var lines = postmot.split('\n');
        var line = lines[0];
        var start_line;
        if (!/\w{2,}/.test(line)) {
            //line 0 only contains farsi synonym
            //append to mosavab
            citation.mosavab += '، ' + nonum_motaradef(line);
            start_line = 1;
        } else {
            //line 0 contains latin and farsi synonyms
            //process it with other lines
            start_line = 0;
        }
        citation.mosavab_motaradef = mosavab_motaradef(lines, start_line);
        citation.biganeh_motaradef = biganeh_motaradef(lines, start_line);
    }
    return citation;
}

function parse(tds) {
    "use strict";
    var citation = {};
    citation.mosavab = nonum_mosavab(tds[0].textContent);
    citation.biganeh = nonum_biganeh(tds[1].textContent);
    debugger;
    citation = parse_tarif(tds[3].textContent, citation);
    citation.hozeh = tds[2].textContent.replace(/[\[\]]/g, '');
    citation.daftar = daftar(tds[4].textContent);
    citation.sarvazheh = tds[0].textContent;
    return citation2string(citation);
}

$(function () {
    "use strict";
    $("tr").slice(1).dblclick(
        function () {
            var tds = $(this).find('td');
            copy_citation(parse(tds));
        }
    );
    $('ul').prepend('<li>برای به دست آوردن <a href="https://fa.wikipedia.org/wiki/%D8%A7%D9%84%DA%AF%D9%88:%DB%8C%D8%A7%D8%AF%DA%A9%D8%B1%D8%AF-%D9%81%D8%B1%D9%87%D9%86%DA%AF%D8%B3%D8%AA%D8%A7%D9%86">یادکرد فرهنگستان</a> جهت استفاده در ویکی‌پدیا کافیست روی ردیفی که می‌خواهید یادکرد آن ساخته شود <a href="https://fa.wikipedia.org/wiki/%D8%AF%D8%A7%D8%A8%D9%84-%DA%A9%D9%84%DB%8C%DA%A9">دوبار-کلیک</a> کنید.</li>');
});
