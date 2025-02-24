//when page is loading:
$(document).ready(function(){
    $('div.manicontent').hide();
    window.mani_TASK = "";
    return false;
});

// RETURN to Sample selection page:
$('input.mani.loaded#sample-name').on('click', function() {
    window.location.href='/auth/user';
    return false;
});

// Get TASK name:
$('button.mani.access.singleqb').on('click', function() { mani_TASK = 'singleqb' });
$('button.mani.access.qubits').on('click', function() { mani_TASK = 'qubits' });

// Benchmark on click > Loading measurement data into Benchmark:
$('#mani-to-benchmark').click( function(){
    $.ajaxSettings.async = false;

    // listimes_singleqb(); accessdata_singleqb();
    // $.getJSON(mssnencrpytonian() + '/mssn/singleqb/access', { wmoment: wmoment }, function (data) { console.log("JOBID: " + JSON.stringify(data.JOBID) ); console.log(data); });

    let quantificationType = ["qfactor_estimation"];
    $.getJSON( '/benchmark/benchmark_getMeasurement', 
    { measurementType: mani_TASK, quantificationType: JSON.stringify(quantificationType) }, 
        function () {
    }); 

    window.open("/benchmark");
    $.ajaxSettings.async = true;
    return false;
    }
);
 
