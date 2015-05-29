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

$(function(){
    $("tr").slice(1).dblclick(
      function(){ 
        tds = $(this).find('td')
        c = '<ref>{{یادکرد فرهنگستان | مصوب=';
        mosavab = tds[0].textContent
        if (!/\d\d$/g.test(mosavab) && !/ \d$/g.test(mosavab)) {
            mosavab = mosavab.replace(/\d$/g, '');
        }
        c += mosavab;
        c += ' | بیگانه=';
        biganeh = tds[1].textContent;
        if (!/\d$/g.test(mosavab)) {
            biganeh = biganeh.replace(/ \d(?=, | \(| ?\/ |$)/g, '');
        }
        c += biganeh;
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
