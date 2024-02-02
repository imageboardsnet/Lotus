document.addEventListener('DOMContentLoaded', function () {

    var options = {
        valueNames: ['name', 'language', 'software']
    };

    var featureList = new List('boards', options);

    document.getElementById('language').addEventListener('change', function () {
        var selection = this.value;
        if (selection) {
            featureList.filter(function(item) {
                return (item.values().language === selection);
            });
        } else {
            featureList.filter();
        }
    });

    document.getElementById('software').addEventListener('change', function () {
        var selection = this.value;
        if (selection) {
            featureList.filter(function(item) {
                var software = item.values().software;
                return (software && software.includes(selection));
            });
        } else {
            featureList.filter();
        }
    });

});

