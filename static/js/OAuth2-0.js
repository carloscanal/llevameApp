// function onSignIn(googleUser) {
//     var profile = googleUser.getBasicProfile();
//     var id_token = googleUser.getAuthResponse().id_token;
//     var csrf_token = getCookie('csrftoken');
    
//     var host = window.location.hostname;

//     var url = '/verifyToken/' + id_token + '/' + profile.getGivenName() + '/' + profile.getFamilyName() + '/' + profile.getEmail() + '/' + profile.getImageUrl();

//     var xhr = new XMLHttpRequest();
//     xhr.open('GET', url, true);
//     xhr.
//     //xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
//     //xhr.setRequestHeader('X-CSRFToken', csrf_token);
//     xhr.onload = function() {
//         window.location.href= '/app';
//     };
//     xhr.send(null);
// }


function signOut() {
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then( function () { console.log('User signed out.'); } );
}