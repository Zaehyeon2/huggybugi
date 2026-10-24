// 웹 대화 알림 받기. 서버 함수 push 가 { title: 보낸 사람, body, face: 보낸 사람 idle 스트립 주소, group } 을 보낸다.
// 아이폰은 받은 푸시마다 알림을 띄워야 한다(안 띄우면 구독을 끊는다). 못 읽어도 띄운다.
// 새 버전이 기다리지 않게 바로 넘긴다. 안 하면 홈 화면 앱을 완전히 닫기 전까지 옛 워커가 푸시를 받는다.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()));

const ICON = './assets/icon-192.png';
// 아이폰은 icon 을 무시하고 앱 아이콘을 쓴다(실기 확인). 얼굴을 받지 않고 바로 띄운다.
const APPLE = /iPhone|iPad|iPod|Macintosh/.test(navigator.userAgent);

// 스트립 첫 칸(높이 = 프레임 한 변)을 4배 nearest 로 키운다.
async function faceIcon(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`face ${res.status}`);
  const img = await createImageBitmap(await res.blob());
  const n = img.height;
  const c = new OffscreenCanvas(n * 4, n * 4);
  const ctx = c.getContext('2d');
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(img, 0, 0, n, n, 0, 0, n * 4, n * 4);
  const bytes = new Uint8Array(
    await (await c.convertToBlob({ type: 'image/png' })).arrayBuffer(),
  );
  let bin = '';
  for (const b of bytes) bin += String.fromCharCode(b);
  return `data:image/png;base64,${btoa(bin)}`;
}

// 앱 아이콘 숫자: 웹 대화를 보기 전까지 받은 알림 수. 대화가 화면에 보이면 페이지(site/push.ts)가 지운다.
async function bump() {
  const c = await caches.open('hd-badge');
  const n = Number((await (await c.match('n'))?.text()) ?? 0) + 1;
  await c.put('n', new Response(String(n)));
  await self.navigator.setAppBadge?.(n);
}

self.addEventListener('push', (e) => {
  let title = '허기부기';
  let body = '';
  let face = '';
  let group = '';
  try {
    const d = e.data?.json();
    title = d?.title || title;
    body = d?.body ?? '';
    face = typeof d?.face === 'string' ? d.face : '';
    group = typeof d?.group === 'string' ? d.group : '';
  } catch {}
  e.waitUntil(
    (async () => {
      // 얼굴을 못 만들거나 늦어도 알림은 띄운다.
      const icon =
        face && !APPLE
          ? await Promise.race([
              faceIcon(face).catch(() => ICON),
              new Promise((r) => setTimeout(() => r(ICON), 3000)),
            ])
          : ICON;
      await self.registration.showNotification(title, {
        body,
        icon,
        badge: './assets/badge-96.png',
        // 그룹마다 한 장으로 바꿔 끼우고, 바뀔 때도 다시 울린다.
        tag: `hd-${group}`,
        renotify: true,
      });
      await bump().catch(() => {});
    })(),
  );
});

// 구독 주소가 바뀌면 새로 받아 두고 표시만 남긴다. 워커엔 로그인 세션이 없어 저장은 다음에 페이지가 열릴 때 site/push.ts 가 한다.
self.addEventListener('pushsubscriptionchange', (e) => {
  e.waitUntil(
    (async () => {
      const key = e.oldSubscription?.options?.applicationServerKey;
      if (!e.newSubscription && key)
        await self.registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: key,
        });
      await (await caches.open('hd-push')).put('changed', new Response('1'));
    })(),
  );
});

self.addEventListener('notificationclick', (e) => {
  e.notification.close();
  e.waitUntil(
    (async () => {
      const url = new URL('./chat', self.location.href).href;
      const open = await self.clients.matchAll({
        type: 'window',
        includeUncontrolled: true,
      });
      const tab = open.find((c) =>
        new URL(c.url).pathname.startsWith(new URL(url).pathname),
      );
      return tab ? tab.focus() : self.clients.openWindow(url);
    })(),
  );
});
