importScripts(
  'https://www.gstatic.com/firebasejs/10.8.0/firebase-app-compat.js',
  'https://www.gstatic.com/firebasejs/10.8.0/firebase-messaging-compat.js'
);

const firebaseConfig = {
  apiKey: "AIzaSyBu62b7CauyuMEtNsy51706v1IiKx1g8Zg",
  authDomain: "sociounido.firebaseapp.com",
  projectId: "sociounido",
  messagingSenderId: "856128232903",
  appId: "1:856128232903:web:3de219f60d2f6bfa7f4de2",
};

firebase.initializeApp(firebaseConfig);
const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  console.log('Alerta recibida con la app cerrada: ', payload);

  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/pwa-192x192.png'
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});