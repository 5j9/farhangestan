function daftar(s) {
    switch(s) {
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
    newstring = '';
    $(string.split('')).each(function() {
        newstring += String.fromCharCode(this.charCodeAt(0) + 1728)
    });
    return newstring
}

function copy_citation(text) {
  window.prompt("برای یادکرد در ویکی‌پدیا رونوشت بردارید:", text);
}

function nonum_mosavab(mosavab) {
    if (!/\d\d$/.test(mosavab) && !/ \d$/.test(mosavab)) {
        return mosavab.replace(/\d$/, '');
    }
    return mosavab;
}

function nonum_motaradef(motaradef) {
    if (!/\d\d$/.test(motaradef)) {
        return motaradef.replace(/ \d$/, '').replace(/ \d،/, '،');
    }
    return motaradef;
}

function nonum_biganeh(biganeh) {
    return biganeh.replace(/ \d(?=, | \(| ?\/ |$)/g, '')
}

$(function(){
    $("tr").slice(1).dblclick(
      function(){ 
        tds = $(this).find('td')
        c = '<ref>{{یادکرد فرهنگستان | مصوب=';
        mosavab = nonum_mosavab(tds[0].textContent)
        tarif = tds[3].textContent
        if (tarif.indexOf('متـ . ') !== -1) {
            //tarif has at list one synonym
            postmot = tarif.split('متـ . ')[1];
            if (postmot.indexOf('*') !== -1) {
                // the star indicates some kind of comment.
                // e.g. واژه * مصوب فرهنگستان اول
                // also see سرگذشت خود
                postmot = nonum_motaradef(postmot.split('*')[0].trim());
            }
            if (!/\w{2,}/i.test(postmot)) {
                //postmot only contains farsi synonym
                c += mosavab + '، ' + nonum_motaradef(postmot);
            }
            else {
                //postmot contains latin and farsi synonyms
                c += mosavab;
                c += ' | مصوب مترادف=';
                // may contain newline. see واکنشگاه هسته‌ای
                motparts = postmot.split('\n');
                firsttime = true;
                for (i=0; i < motparts.length; i++) {
                    part = motparts[i].trim()
                    if (!part) continue
                    // [\u0600-\u06FF] is the Arabic (Unicode block)
                    // https://en.wikipedia.org/wiki/Arabic_%28Unicode_block%29
                    mosavab_motaradef = /[\u0600-\u06FF \u200c]+/.exec(part);
                    if (!mosavab_motaradef) continue;
                    mosavab_motaradef = mosavab_motaradef[0].trim();
                    if (!mosavab_motaradef) continue;
                    if (firsttime) {
                        c += nonum_mosavab(mosavab_motaradef);
                        firsttime = false;
                    }
                    else {
                        c += '، ' + nonum_mosavab(mosavab_motaradef);
                    }
                }
                c += ' | بیگانهٔ مترادف=';
                firsttime = true
                for (i=0; i < motparts.length; i++) {
                    part = motparts[i].trim();
                    if (!part) continue;
                    biganeh_motaradef = /\w{2,}[ \w-]*(?=$|[\u0600-\u06FF\u200c])/.exec(part);
                    if (!biganeh_motaradef) continue;
                    biganeh_motaradef = biganeh_motaradef[0].trim();
                    if (!biganeh_motaradef) continue;
                    if (firsttime) {
                        c += nonum_biganeh(biganeh_motaradef);
                        firsttime = false;
                    }
                    else {
                        c += ', ' + nonum_biganeh(biganeh_motaradef);
                    }                    
                }
                c += ' | بیگانه در فارسی مترادف=';
            }
        }
        c += ' | بیگانه=';
        biganeh = nonum_biganeh(tds[1].textContent);
        c += biganeh;
        c += ' | بیگانه در فارسی=';
        c += ' | حوزه=';
        c += tds[2].textContent.replace(/[\[\]]/g, '');
        c += ' | دفتر=';
        c += daftar(tds[4].textContent);
        c += ' | بخش=فارسی'
        c += ' | سرواژه=';
        c += tds[0].textContent;
        c += ' }}</ref>';
        copy_citation(c); 
      }
    );
    $('ul').prepend('<li>برای به دست آوردن <a href="https://fa.wikipedia.org/wiki/%D8%A7%D9%84%DA%AF%D9%88:%DB%8C%D8%A7%D8%AF%DA%A9%D8%B1%D8%AF-%D9%81%D8%B1%D9%87%D9%86%DA%AF%D8%B3%D8%AA%D8%A7%D9%86">یادکرد فرهنگستان</a> جهت استفاده در ویکی‌پدیا کافیست روی ردیفی که می‌خواهید یادکرد آن ساخته شود <a href="https://fa.wikipedia.org/wiki/%D8%AF%D8%A7%D8%A8%D9%84-%DA%A9%D9%84%DB%8C%DA%A9">دوبار-کلیک</a> کنید.</li>');
})
