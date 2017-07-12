var donotclose = function () {
    $('.overlay').show();
    $('.uploadWin').show();
}

var disable_input = function (container) {
    container.find("input").prop('disabled', true);
    container.hide();
}

var enable_input = function (container) {
    container.find("input").prop('disabled', false);
    container.show();
}

function endsWith(str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
}

$(document).ready(function () {
        var mode = $("#contributionmode input[type='radio']:checked").val();
        if (mode == "uploadzip") {
            disable_input($("#resourceurl"));
            enable_input($("#fileupload"));
        } else if (mode == "url") {
            disable_input($("#fileupload"));
            enable_input($("#resourceurl"));
        }
    }
);

$(function () {
        $("#contributionmode input[type='radio']").change(function () {
            mode = $(this).val();
            if (mode == "uploadzip") {
                disable_input($("#resourceurl"));
                enable_input($("#fileupload"));
            } else if (mode == "url") {
                disable_input($("#fileupload"));
                enable_input($("#resourceurl"));
            }
        })
    }
)

$(function () {
    $('form').submit(function (event) {
        var file = $('#filebutton')[0].files[0];
        if (file !== undefined && file.size > 104857600) {
            alert("The file you are trying to upload is larger " +
                "than the maximum upload file size (100mb).\n" +
                "Please contact elrc-share@ilsp.gr");
            return false;
        }
        return true;
    })
});

var isIE = /*@cc_on!@*/false || !!document.documentMode;


if (!isIE) {
    $(function () {
        var bar = $('.bar');
        var percent = $('.percent');
        var status = $('#status');
        var ok = $('#ok');
        $('form').ajaxForm({
            beforeSend: function (xhr, opts) {
                var mode = $("#contributionmode input[type='radio']:checked").val();
                if (mode == undefined) {
                    xhr.abort();
                    alert("Please select a contribution mode!");
                    return false
                }
                if (mode == "uploazip") {
                    var fileName = $('input[type=file]').val().split('/').pop().split('\\').pop();
                    if (!endsWith(fileName, ".zip")) {
                        xhr.abort();
                        alert("The file you are trying to upload does not have a .zip extension.\n" +
                            "Please make sure that you properly compress your data into a valid .zip file before uploading.");
                        return false
                    }
                }
                status.removeClass("success");
                if (mode == "url") {
                    var url = $('input[id=resourceUrl]').val();
                    if (validateURL(url)) {
                            status.html("<i class='fa fa-spinner fa-pulse' aria-hidden='true'></i> Submitting your contribution: \nPlease wait...");
                        } else {
                        alert("Please enter a valid URL!");
                        xhr.abort();
                        return false;
                    }
                } else {
                    status.html("<i class='fa fa-spinner fa-pulse' aria-hidden='true'></i> Uploading file: \"" + fileName + "\".\nPlease wait...");
                }
                ok.hide();
                donotclose();
                var percentVal = '0%';
                bar.width(percentVal);
                percent.html(percentVal);

            },
            uploadProgress: function (event, position, total, percentComplete) {
                var percentVal = percentComplete + '%';
                bar.width(percentVal);
                percent.html(percentVal);
            },
            error: function () {
                $('.uploadWin').hide();
                $('.overlay').hide();
                alert("There was an error uploading this file.\n" +
                    "Please make sure that you are trying to upload a valid '.zip' file.\n" +
                    "If the problem persists please try again later.");
            },
            complete: function (response) {
                var json_response = $.parseJSON(response.responseText);
                if (json_response.status == 'failed') {
                    status.addClass("failure")
                    bar.hide();
                    percent.hide();
                    $(".progress").hide();
                } else {
                    status.removeClass("failure");
                    status.addClass("success");
                    $('form').clearForm();
                }
                status.html(json_response.message);
                ok.show();
                //location.reload();
            },

        });
    });
}
else {
    $(function () {
        var bar = $('.bar');
        var percent = $('.percent');
        var status = $('#status');
        var ok = $('#ok');
        $('form').submit(function (event) {
            event.preventDefault();
            $.ajax({
                cache: false,
                url: "/repository/contribute",
                type: "POST",
                data: new FormData($('form')[0]),
                contentType: false,
                processData: false,
                dataType: "text",
                beforeSend: function (xhr, opts) {
                    var mode = $("#contributionmode input[type='radio']:checked").val();
                    if (mode == undefined) {
                        xhr.abort();
                        alert("Please select a contribution mode!")
                        return false
                    } else {
                        alert(mode);
                    }
                    var fileName = $('input[type=file]').val().split('/').pop().split('\\').pop();
                    if (!endsWith(fileName, ".zip")) {
                        xhr.abort();
                        alert("The file you are trying to upload does not have a .zip extension.\n" +
                            "Please make sure that you properly compress your data into a valid .zip file before uploading.");
                        return false
                    }
                    status.removeClass("success");
                    if (mode == "url") {
                        var url = $('input[id=resourceUrl]').val();
                        if (validateURL(url)) {
                            status.html("<i class='fa fa-spinner' aria-hidden='true'></i> Submitting your contribution: \nPlease wait...");
                        } else {
                            alert("Please enter a valid URL!");
                            xhr.abort();
                            return false;
                        }
                    } else {
                        status.html("<i class='fa fa-spinner fa-pulse' aria-hidden='true'></i> Uploading file: \"" + fileName + "\".\nPlease wait...");
                    }
                    ok.hide();
                    donotclose();
                    var percentVal = '0%';
                    bar.width(percentVal);
                    percent.html(percentVal);
                },
                xhr: function () {
                    var xhr = $.ajaxSettings.xhr();
                    xhr.upload.onprogress = function (e) {
                        var percentVal = Math.floor(e.loaded / e.total * 100) + '%';
                        bar.width(percentVal);
                        percent.html(percentVal);
                    };
                    return xhr;
                },
                success: function (responseData) {
                    var json_response = $.parseJSON(responseData);
                    if (json_response.status == 'failed') {
                        status.addClass("failure")
                        bar.hide();
                        percent.hide();
                        $(".progress").hide();
                    } else {
                        status.removeClass("failure");
                        status.addClass("success");
                        $('form').clearForm();
                    }
                    status.html(json_response.message);
                    ok.show();
                },
                // error: function (responseData, textStatus, errorThrown) {
                //     alert("error: " + textStatus);
                // },
                // complete: function (xhr) {
                //     if (xhr.status == 200) {
                //         alert("ok");
                //     }
                // }
            });
        });
        return false;
    });
}

function validateURL(value) {
    return /^(https?|ftp):\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?)(:\d*)?)(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(\#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i.test(value);
}