// $("#start").click(function () {
//     let loc = window.location;
//     let btn = $(this);
//     console.log({ "player": loc.pathname.split("/")[2]});
//     $.get( "/startgame", function() {
//       })
//         .done(function(res) {
//           update();
//         })
// })
$(document).ready(() => {
    console.log($("#buttons").has("#start").length);
    if ($("#buttons").has("#start").length == 0) {
        start = 1
        update()
    }
})

let start = 0
function update() {
    if (start != 0) {
        let s = Number($("#sec").text());
        let m = Number($("#min").text());
        if (s < 60) {
            s++
            let text = String(s)
            $("#sec").text(text)
        } else {
            m++
            s = 0
            let text = String(m)
            $("#min").text(text)
        }
        setTimeout(() => {
            update()
        }, 1000);
    }
}

$("#start").click(() => {
    $.get("/startgame")
        .then((response) => {
            if (!$("#danger").hasClass("d-none")) {
                $("#danger").addCLass("d-none").text("")
            }
            start = 1
            update()
            $("#end").removeClass("d-none")
            $("#start").remove()
        })
        .catch((err) => {
            $("#danger").removeClass("d-none").text(err)
        })
})

$("#end").click(() => {
    start = 0
    $.get("/stopgame")
})