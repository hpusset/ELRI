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

function resetMessages() {
    $('.uploadWin').hide();
    $('.overlay').hide();
    $('#status').removeClass();
    $('#status').html("");
}

$(function () {
    if ($("#licence").find("option:selected").val() ===
        "non-standard/Other_Licence/Terms") {
        enable_input($("#licencefile"));
    }
    else {
        disable_input($("#licencefile"));
    }
});

$(function () {
    $("#licence").change(
        function () {
            licence = $(this).find("option:selected").val();
            if (licence === "non-standard/Other_Licence/Terms") {
                enable_input($("#licencefile"));
            }
            else {
                disable_input($("#licencefile"));
            }
        }
    );
});

$(function () {
    $("option[data-toggle='tooltip']").mouseenter(
        function () {
            $(this).tooltip('show');
        }
    );

    $("option[data-toggle='tooltip']").mouseleave(
        function () {
            $(this).tooltip('hide');
        }
    );
});

$(function () {
    $('form').submit(function (event) {
        var file = $('#filebutton')[0].files[0];
        if (file !== undefined && file.size > 104857600) {
            alert(gettext("The file(s) you are trying to upload exceed(s) the size limit. If the file(s) you would like to contribute exceed(s) 100.0 MB, please contact us to provide an SFTP link for direct download or consider uploading smaller files."));
            return false;
        }
        return true;
    })
});

var isIE = /*@cc_on!@*/false || !!document.documentMode;

var acceptedExtensions = [".zip", ".pdf", ".doc", ".docx", ".rtf", ".tmx", ".txt", ".xls", ".xlsx", ".xml", ".sdltm", ".odt", ".tbx"];

if (!isIE) {
    $(function () {
        var bar = $('.bar');
        var percent = $('.percent');
        var status = $('#status');
        var ok = $('#ok');
        $('form').ajaxForm({
            beforeSend: function (xhr, opts) {
                var fileName = $('#filebutton').val().split('/').pop().split('\\').pop();
                if (!$.grep(acceptedExtensions, function (el) {return endsWith(fileName, el)})) {
                    xhr.abort();
                    alert(gettext("Only files of type ") + acceptedExtensions.join(", ") +
                        gettext(" are allowed. The .zip files can only contain files of the specified types. Please consider removing the files that do not belong to one of these types."));
                    return false
                }
                status.html("<i class='fa fa-spinner fa-pulse' aria-hidden='true'></i>"+gettext(" Uploading file: \"" + fileName + "\".\nPlease wait..."));
                status.removeClass("success");
                ok.hide();
                donotclose();
                var percentVal = '0%';
                bar.width(percentVal);
                percent.html(percentVal);

            },
            uploadProgress: function (event, position, total, percentComplete) {
                var percentVal = percentComplete + '%';
                bar.show();
                percent.show();
                $(".progress").show();
                bar.width(percentVal);
                percent.html(percentVal);
            },
            error: function () {
                $('.uploadWin').hide();
                $('.overlay').hide();
                alert(gettext("There was an error uploading this file.\n" +
                    "Please make sure that you are trying to upload a file with a valid extension.\n" +
                    "If the problem persists please try again later."));
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
                    var fileName = $('input[type=file]').val().split('/').pop().split('\\').pop();
                    if (!$.grep(acceptedExtensions, function (el) {return endsWith(fileName, el)})) {
                        xhr.abort();
                        alert(gettext("Only files of type ") + acceptedExtensions.join(", ") +
                            gettext(" are allowed. The .zip files can only contain files of the specified types. Please consider removing the files that do not belong to one of these types."));
                        return false
                    }
                    status.removeClass("success");
                    status.html("<i class='fa fa-spinner fa-pulse' aria-hidden='true'></i>" + gettext("Uploading file: \"" + fileName + "\".\nPlease wait..."));
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
            $('.uploadWin').hide();
            $('.overlay').hide();

        });
        return false;
    });
}


function validateURL(value) {
    return /^(https?|ftp):\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?)(:\d*)?)(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(\#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i.test(value);
}
