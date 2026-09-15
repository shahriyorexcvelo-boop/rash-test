/**
 * ASOSIY MINI APP — app.js
 * PIN tizimi, tab navigatsiya, API, Til, Tema
 */

const API_BASE = '';
const LS_PIN = 'app_pin';
const LS_USER = 'app_user';
const LS_LANG = 'app_lang';
const LS_THEME = 'app_theme';

// ── I18N ────────────────────────────────────────
var I18N = {
  uz: {
    tab_home:'Asosiy', tab_tests:'Testlar', tab_profile:'Profil', tab_admin:'Admin',
    pin_create:'PIN kod yarating', pin_create_sub:'Xavfsizlik uchun 4 xonali PIN kod belgilang',
    pin_confirm:'PIN kodni tasdiqlang', pin_confirm_sub:'Tasdiqlash uchun PIN kodingizni qayta kiriting',
    pin_enter_sub:'Kirish uchun PIN kodingizni kiriting',
    pin_mismatch:'PIN kodlar mos kelmadi', pin_wrong:"Noto\u02BBg\u02BBri PIN kod",
    welcome:'Xush kelibsiz',
    home_title:'Asosiy', home_sub:'Testlar va rejalar',
    active_tests:'FAOL TESTLAR', closed_tests:"TO\u02BBXTATILGAN",
    already_done:'Allaqachon topshirildi', start_test:'Testni boshlash',
    my_tests_title:'Mening testlarim', tests_count:'ta test topshirildi',
    empty_tests:'Hali hech qanday test topshirmadingiz',
    empty_active:"Hozircha faol test yo\u02BBq",
    profile_title:'Profil', change_pin:"PIN kodni o\u02BBzgartirish",
    stat_tests:'Testlar', stat_avg:"O\u02BBrtacha", stat_max:'Eng yuqori', stat_status:'Holat',
    info_name:"To\u02BBlliq ism", info_phone:'Telefon', info_tg:'Telegram', info_id:'TG ID',
    status_new:"Yangi o\u02BBquvchi", status_gold:'Oltin', status_silver:'Kumush',
    status_bronze:'Bronza', status_learner:"O\u02BBrganuvchi",
    result_title:'Natija', result_correct:"To\u02BBg\u02BBri", result_wrong:"Noto\u02BBg\u02BBri",
    result_blank:'Belgilanmagan', result_date:'Sana', result_grade:'Daraja',
    users_title:'Foydalanuvchilar', total:'Jami', approved:'Tasdiqlangan', pending:'Kutayotgan',
    create_test:'Test yaratish', admin_panel:'Admin Panel', grade_lbl:'daraja',
    theme_dark:'Tungi', theme_light:'Kunduzgi'
  },
  ru: {
    tab_home:'\u0413\u043b\u0430\u0432\u043d\u0430\u044f', tab_tests:'\u0422\u0435\u0441\u0442\u044b', tab_profile:'\u041f\u0440\u043e\u0444\u0438\u043b\u044c', tab_admin:'\u0410\u0434\u043c\u0438\u043d',
    pin_create:'\u0421\u043e\u0437\u0434\u0430\u0439\u0442\u0435 PIN', pin_create_sub:'\u0412\u0432\u0435\u0434\u0438\u0442\u0435 4-\u0437\u043d\u0430\u0447\u043d\u044b\u0439 PIN \u0434\u043b\u044f \u0431\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0441\u0442\u0438',
    pin_confirm:'\u041f\u043e\u0434\u0442\u0432\u0435\u0440\u0434\u0438\u0442\u0435 PIN', pin_confirm_sub:'\u0412\u0432\u0435\u0434\u0438\u0442\u0435 PIN \u0435\u0449\u0451 \u0440\u0430\u0437',
    pin_enter_sub:'\u0412\u0432\u0435\u0434\u0438\u0442\u0435 PIN-\u043a\u043e\u0434 \u0434\u043b\u044f \u0432\u0445\u043e\u0434\u0430',
    pin_mismatch:'PIN-\u043a\u043e\u0434\u044b \u043d\u0435 \u0441\u043e\u0432\u043f\u0430\u0434\u0430\u044e\u0442', pin_wrong:'\u041d\u0435\u0432\u0435\u0440\u043d\u044b\u0439 PIN-\u043a\u043e\u0434',
    welcome:'\u0414\u043e\u0431\u0440\u043e \u043f\u043e\u0436\u0430\u043b\u043e\u0432\u0430\u0442\u044c',
    home_title:'\u0413\u043b\u0430\u0432\u043d\u0430\u044f', home_sub:'\u0422\u0435\u0441\u0442\u044b \u0438 \u043f\u043b\u0430\u043d\u044b',
    active_tests:'\u0410\u041a\u0422\u0418\u0412\u041d\u042b\u0415 \u0422\u0415\u0421\u0422\u042b', closed_tests:'\u0417\u0410\u0412\u0415\u0420\u0428\u0415\u041d\u042b',
    already_done:'\u0423\u0436\u0435 \u0441\u0434\u0430\u043d', start_test:'\u041d\u0430\u0447\u0430\u0442\u044c \u0442\u0435\u0441\u0442',
    my_tests_title:'\u041c\u043e\u0438 \u0442\u0435\u0441\u0442\u044b', tests_count:'\u0442\u0435\u0441\u0442\u043e\u0432 \u0441\u0434\u0430\u043d\u043e',
    empty_tests:'\u0412\u044b \u0435\u0449\u0451 \u043d\u0435 \u0441\u0434\u0430\u0432\u0430\u043b\u0438 \u043d\u0438 \u043e\u0434\u043d\u043e\u0433\u043e \u0442\u0435\u0441\u0442\u0430',
    empty_active:'\u041f\u043e\u043a\u0430 \u043d\u0435\u0442 \u0430\u043a\u0442\u0438\u0432\u043d\u044b\u0445 \u0442\u0435\u0441\u0442\u043e\u0432',
    profile_title:'\u041f\u0440\u043e\u0444\u0438\u043b\u044c', change_pin:'\u0418\u0437\u043c\u0435\u043d\u0438\u0442\u044c PIN-\u043a\u043e\u0434',
    stat_tests:'\u0422\u0435\u0441\u0442\u044b', stat_avg:'\u0421\u0440\u0435\u0434\u043d\u0435\u0435', stat_max:'\u041c\u0430\u043a\u0441\u0438\u043c\u0443\u043c', stat_status:'\u0421\u0442\u0430\u0442\u0443\u0441',
    info_name:'\u041f\u043e\u043b\u043d\u043e\u0435 \u0438\u043c\u044f', info_phone:'\u0422\u0435\u043b\u0435\u0444\u043e\u043d', info_tg:'Telegram', info_id:'TG ID',
    status_new:'\u041d\u043e\u0432\u044b\u0439 \u0443\u0447\u0435\u043d\u0438\u043a', status_gold:'\u0417\u043e\u043b\u043e\u0442\u043e', status_silver:'\u0421\u0435\u0440\u0435\u0431\u0440\u043e',
    status_bronze:'\u0411\u0440\u043e\u043d\u0437\u0430', status_learner:'\u041e\u0431\u0443\u0447\u0430\u044e\u0449\u0438\u0439\u0441\u044f',
    result_title:'\u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442', result_correct:'\u041f\u0440\u0430\u0432\u0438\u043b\u044c\u043d\u044b\u0435', result_wrong:'\u041d\u0435\u043f\u0440\u0430\u0432\u0438\u043b\u044c\u043d\u044b\u0435',
    result_blank:'\u041d\u0435 \u043e\u0442\u043c\u0435\u0447\u0435\u043d\u043e', result_date:'\u0414\u0430\u0442\u0430', result_grade:'\u0423\u0440\u043e\u0432\u0435\u043d\u044c',
    users_title:'\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0438', total:'\u0412\u0441\u0435\u0433\u043e', approved:'\u041f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u044b', pending:'\u041e\u0436\u0438\u0434\u0430\u044e\u0442',
    create_test:'\u0421\u043e\u0437\u0434\u0430\u0442\u044c \u0442\u0435\u0441\u0442', admin_panel:'\u041f\u0430\u043d\u0435\u043b\u044c \u0430\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440\u0430',
    grade_lbl:'\u0443\u0440\u043e\u0432\u0435\u043d\u044c', theme_dark:'\u0422\u0451\u043c\u043d\u0430\u044f', theme_light:'\u0421\u0432\u0435\u0442\u043b\u0430\u044f'
  },
  en: {
    tab_home:'Home', tab_tests:'Tests', tab_profile:'Profile', tab_admin:'Admin',
    pin_create:'Create PIN Code', pin_create_sub:'Set a 4-digit PIN for security',
    pin_confirm:'Confirm PIN', pin_confirm_sub:'Enter your PIN again to confirm',
    pin_enter_sub:'Enter your PIN to sign in',
    pin_mismatch:"PIN codes don't match", pin_wrong:'Wrong PIN code',
    welcome:'Welcome',
    home_title:'Home', home_sub:'Tests and schedules',
    active_tests:'ACTIVE TESTS', closed_tests:'CLOSED',
    already_done:'Already submitted', start_test:'Start test',
    my_tests_title:'My Tests', tests_count:'tests submitted',
    empty_tests:"You haven't submitted any tests yet",
    empty_active:'No active tests right now',
    profile_title:'Profile', change_pin:'Change PIN Code',
    stat_tests:'Tests', stat_avg:'Average', stat_max:'Best', stat_status:'Status',
    info_name:'Full name', info_phone:'Phone', info_tg:'Telegram', info_id:'TG ID',
    status_new:'New student', status_gold:'Gold', status_silver:'Silver',
    status_bronze:'Bronze', status_learner:'Learner',
    result_title:'Result', result_correct:'Correct', result_wrong:'Wrong',
    result_blank:'Blank', result_date:'Date', result_grade:'Grade',
    users_title:'Users', total:'Total', approved:'Approved', pending:'Pending',
    create_test:'Create test', admin_panel:'Admin Panel',
    grade_lbl:'grade', theme_dark:'Dark', theme_light:'Light'
  }
};

function t(key) {
  var lang = localStorage.getItem(LS_LANG) || 'uz';
  return (I18N[lang] && I18N[lang][key]) || (I18N.uz && I18N.uz[key]) || key;
}

// ── STATE ────────────────────────────────────────
var state = {
  tgUser: null,
  userInfo: null,
  isAdmin: false,
  pinBuffer: '',
  pinMode: 'enter',
  pinFirst: '',
  activeTab: 'home',
};

// ── INIT ────────────────────────────────────────
function initApp() {
  // Tema va tilni DARHOL yuklash
  var savedTheme = localStorage.getItem(LS_THEME) || 'dark';
  document.documentElement.setAttribute('data-theme', savedTheme);
  updateThemeIcon(savedTheme);
  updateLangLabel();

  try {
    var tg = window.Telegram && window.Telegram.WebApp;
    if (tg) { tg.ready(); tg.expand(); }
    var tgU = tg && tg.initDataUnsafe && tg.initDataUnsafe.user;
    var urlParams = new URLSearchParams(window.location.search);
    var urlUserId = parseInt(urlParams.get('user_id') || '0');
    if (tgU && tgU.id) {
      state.tgUser = tgU;
    } else if (urlUserId) {
      state.tgUser = { id: urlUserId, first_name: 'Foydalanuvchi', last_name: '', username: '' };
    } else {
      state.tgUser = { id: 0, first_name: 'Foydalanuvchi', last_name: '', username: '' };
    }
    try {
      var saved = localStorage.getItem(LS_USER);
      if (saved) state.userInfo = JSON.parse(saved);
    } catch (e) {}
  } catch (err) {
    console.error('initApp error:', err);
  }

  runSplash();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}

// ── SPLASH ──────────────────────────────────────
function runSplash() {
  var splash = document.getElementById('splash-screen');
  var logoBox = document.getElementById('splash-logo-box');
  var logoImg = document.getElementById('splash-logo-img');
  var check = document.getElementById('splash-check');
  var ring = document.getElementById('splash-ring');
  var ring2 = document.getElementById('splash-ring-2');

  if (!splash) { initPinScreen(); return; }

  // 2.2s — checkmark
  setTimeout(function() {
    if (logoBox) logoBox.classList.add('success');
    if (ring) ring.classList.add('success');
    if (ring2) ring2.classList.add('success');
  }, 2200);

  // 3.5s — PIN ga o'tish
  setTimeout(function() {
    if (splash) splash.classList.add('hide-splash');
    var pinScreen = document.getElementById('pin-screen');
    if (pinScreen) pinScreen.style.display = 'flex';
    initPinScreen();
    setTimeout(function() {
      if (splash) splash.style.display = 'none';
    }, 650);
  }, 3500);
}

// ── PIN SYSTEM ──────────────────────────────────
function initPinScreen() {
  var hasPin = !!localStorage.getItem(LS_PIN);
  var pinTitle = document.getElementById('pin-title');
  var pinSub = document.getElementById('pin-subtitle');

  if (!hasPin) {
    state.pinMode = 'setup';
    pinTitle.textContent = t('pin_create');
    pinSub.textContent = t('pin_create_sub');
  } else {
    state.pinMode = 'enter';
    var name = (state.userInfo && state.userInfo.fullname)
      || (state.tgUser && state.tgUser.first_name) || 'Salom';
    pinTitle.textContent = t('welcome') + ', ' + name.split(' ')[0] + '!';
    pinSub.textContent = t('pin_enter_sub');
  }
  renderPinDots(0);
}

function onPinKey(val) {
  if (state.pinBuffer.length >= 4) return;
  state.pinBuffer += val;
  renderPinDots(state.pinBuffer.length);
  if (state.pinBuffer.length === 4) setTimeout(processPin, 120);
}

function onPinDel() {
  if (state.pinBuffer.length === 0) return;
  state.pinBuffer = state.pinBuffer.slice(0, -1);
  renderPinDots(state.pinBuffer.length);
}

function renderPinDots(count, mode) {
  var dots = document.querySelectorAll('.pin-dot');
  dots.forEach(function(d, i) {
    d.classList.remove('filled', 'error');
    if (mode === 'error') { d.classList.add('error'); }
    else if (i < count) { d.classList.add('filled'); }
  });
}

function processPin() {
  var pin = state.pinBuffer;
  state.pinBuffer = '';

  if (state.pinMode === 'setup') {
    state.pinFirst = pin;
    state.pinMode = 'confirm';
    document.getElementById('pin-title').textContent = t('pin_confirm');
    document.getElementById('pin-subtitle').textContent = t('pin_confirm_sub');
    renderPinDots(0);
    showPinError('');
  } else if (state.pinMode === 'confirm') {
    if (pin === state.pinFirst) {
      localStorage.setItem(LS_PIN, btoa(pin));
      showPinError('');
      launchApp();
    } else {
      showPinError(t('pin_mismatch'));
      renderPinDots(4, 'error');
      state.pinMode = 'setup';
      state.pinFirst = '';
      setTimeout(function() {
        renderPinDots(0);
        document.getElementById('pin-title').textContent = t('pin_create');
        document.getElementById('pin-subtitle').textContent = t('pin_create_sub');
        showPinError('');
      }, 1000);
    }
  } else {
    var stored = '';
    try { stored = atob(localStorage.getItem(LS_PIN) || ''); } catch(e) {}
    if (pin === stored) {
      showPinError('');
      launchApp();
    } else {
      showPinError(t('pin_wrong'));
      renderPinDots(4, 'error');
      setTimeout(function() { renderPinDots(0); showPinError(''); }, 900);
    }
  }
}

function showPinError(msg) {
  var el = document.getElementById('pin-error');
  if (el) el.textContent = msg;
}

// ── LAUNCH APP ──────────────────────────────────
async function launchApp() {
  var pinScreen = document.getElementById('pin-screen');
  pinScreen.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
  pinScreen.style.opacity = '0';
  pinScreen.style.transform = 'scale(0.96)';
  setTimeout(function() { pinScreen.style.display = 'none'; }, 350);

  var app = document.getElementById('app');
  app.style.display = 'flex';
  app.style.flexDirection = 'column';
  app.classList.add('visible');

  applyI18n();

  try { await loadUserProfile(); } catch(e) { console.warn('Profile:', e); }
  updateHeaderUser();
  switchTab('home');
}

// ── API ─────────────────────────────────────────
async function apiGet(path) {
  var res = await fetch(API_BASE + path);
  if (!res.ok) throw new Error('API ' + res.status);
  return res.json();
}

async function loadUserProfile() {
  var tgId = state.tgUser && state.tgUser.id;
  if (!tgId) return;
  try {
    var data = await apiGet('/api/app/profile?tg_id=' + tgId);
    if (data.success) {
      state.userInfo = data.user;
      state.isAdmin = data.is_admin;
      localStorage.setItem(LS_USER, JSON.stringify(data.user));
      var adminTab = document.getElementById('nav-admin');
      if (adminTab) adminTab.style.display = state.isAdmin ? 'flex' : 'none';
      if (state.isAdmin && data.pending_users > 0) {
        var badge = document.getElementById('admin-badge');
        if (badge) { badge.textContent = data.pending_users; badge.style.display = 'block'; }
      }
    }
  } catch (e) { console.warn('loadUserProfile err:', e); }
}

async function loadActiveTests() {
  var tab = document.getElementById('tab-home');
  tab.innerHTML = '<div class="skeleton skeleton-card"></div><div class="skeleton skeleton-card"></div>';
  try {
    var tgId = (state.tgUser && state.tgUser.id) || 0;
    var data = await apiGet('/api/app/active-tests?tg_id=' + tgId);
    if (data.success) renderHomeTab(data.tests);
    else throw new Error('no success');
  } catch (e) {
    tab.innerHTML = '<div class="empty-state"><div class="empty-icon">\u26A0\uFE0F</div><p>' + t('empty_active') + '</p></div>';
  }
}

async function loadMyResults() {
  var tab = document.getElementById('tab-tests');
  tab.innerHTML = '<div class="skeleton skeleton-card"></div><div class="skeleton skeleton-card"></div>';
  try {
    var tgId = (state.tgUser && state.tgUser.id) || 0;
    var data = await apiGet('/api/app/my-results?tg_id=' + tgId);
    if (data.success) renderTestsTab(data.results);
    else throw new Error('no success');
  } catch (e) {
    tab.innerHTML = '<div class="empty-state"><div class="empty-icon">\u26A0\uFE0F</div><p>' + t('empty_tests') + '</p></div>';
  }
}

async function loadAllUsers() {
  try {
    var tgId = (state.tgUser && state.tgUser.id) || 0;
    var data = await apiGet('/api/app/users?tg_id=' + tgId);
    if (data.success) renderUsersSection(data.users, data.stats);
  } catch (e) { console.warn('users err:', e); }
}

// ── TAB NAVIGATION ──────────────────────────────
function switchTab(tabId) {
  state.activeTab = tabId;
  document.querySelectorAll('.nav-item').forEach(function(el) {
    el.classList.toggle('active', el.dataset.tab === tabId);
  });
  document.querySelectorAll('.tab-content').forEach(function(el) {
    el.classList.toggle('active', el.id === 'tab-' + tabId);
  });
  if (tabId === 'home') loadActiveTests();
  else if (tabId === 'tests') loadMyResults();
  else if (tabId === 'profile') renderProfileTab();
  else if (tabId === 'admin') { renderAdminTab(); loadAllUsers(); }
}

// ── HOME TAB (faqat faol testlar, planned YO'Q) ─
function renderHomeTab(tests) {
  var tab = document.getElementById('tab-home');
  var tgId = (state.tgUser && state.tgUser.id) || 0;

  // Faqat faol testlar (is_planned=false, is_active=true), va faol bo'lmaganlar
  var active = tests.filter(function(t) { return t.is_active && !t.is_planned; });
  var inactive = tests.filter(function(t) { return !t.is_active && !t.is_planned; });

  var html = '<div class="section-header animate-in">' +
    '<div class="section-title">' + t('home_title') + '</div>' +
    '<div class="section-sub">' + t('home_sub') + '</div></div>';

  if (active.length > 0) {
    html += '<div class="section-sub" style="margin-bottom:10px;font-weight:700;color:var(--success);font-size:12px;">\u2705 ' + t('active_tests') + '</div>';
    active.forEach(function(test, i) {
      var done = test.already_submitted;
      html += '<div class="card animate-in" style="animation-delay:' + (i * 0.06) + 's">' +
        '<div class="card-header">' +
        '<div class="card-icon blue">\uD83D\uDCD0</div>' +
        '<div style="flex:1;min-width:0">' +
        '<div class="card-title">' + escHtml(test.title) + '</div>' +
        '<div class="card-meta"><span>' + escHtml(test.test_code) + '</span><span>\u2022</span><span>' + (test.total_questions || 45) + ' savol</span>' +
        (test.time_limit_min ? '<span>\u2022</span><span>\u23F1 ' + test.time_limit_min + ' daq</span>' : '') + '</div>' +
        '</div>' +
        '<span class="badge ' + (done ? 'badge-inactive' : 'badge-active') + '">' + (done ? '\u2705 ' + t('already_done') : '\uD83D\uDFE2 Faol') + '</span>' +
        '</div>';

      if (done) {
        html += '<div style="text-align:center;padding:8px 0 4px;font-size:13px;color:var(--text-muted);">\u2705 ' + t('already_done') + '</div>';
      } else {
        // Testni mini ilovada ochish o'rniga, faqat bot orqali ishlash haqida xabar
        html += '<div style="text-align:center;padding:8px 0 4px;font-size:13px;color:var(--text-muted);font-weight:600;">Testni bot orqali ishlashingiz mumkin</div>';
      }
      html += '</div>';
    });
  }

  if (active.length === 0) {
    html += '<div class="empty-state animate-in"><div class="empty-icon">\uD83D\uDCED</div><p>' + t('empty_active') + '</p></div>';
  }

  if (inactive.length > 0) {
    html += '<div class="divider"></div><div class="section-sub" style="margin-bottom:10px;font-size:12px;color:var(--text-muted);">\uD83D\uDD12 ' + t('closed_tests') + '</div>';
    inactive.forEach(function(test) {
      html += '<div class="card" style="opacity:0.55"><div class="card-header">' +
        '<div class="card-icon red">\uD83D\uDD12</div>' +
        '<div style="flex:1"><div class="card-title">' + escHtml(test.title) + '</div>' +
        '<div class="card-meta">' + escHtml(test.test_code) + '</div></div>' +
        '<span class="badge badge-inactive">To\'xtatildi</span></div></div>';
    });
  }

  tab.innerHTML = html;
}

// ── TESTS TAB (faqat topshirilgan, bosilsa natija) ─
function renderTestsTab(results) {
  var tab = document.getElementById('tab-tests');
  var html = '<div class="section-header animate-in">' +
    '<div class="section-title">' + t('my_tests_title') + '</div>' +
    '<div class="section-sub">' + results.length + ' ' + t('tests_count') + '</div></div>';

  if (results.length === 0) {
    html += '<div class="empty-state animate-in"><div class="empty-icon">\uD83D\uDCED</div><p>' + t('empty_tests') + '</p></div>';
  } else {
    window._myResults = results;
    results.forEach(function(r, i) {
      var score = (r.score != null) ? r.score : 0;
      var maxScore = r.max_score || 100;
      var grade = r.grade || getGradeFromScore(score, maxScore);
      var gradeClass = gradeToClass(grade);
      var date = formatDate(r.submitted_at);
      html += '<div class="history-card animate-in" style="animation-delay:' + (i * 0.05) + 's;cursor:pointer" onclick="showResultModal(window._myResults[' + i + '])">' +
        '<div class="history-info" style="padding-left:12px">' +
        '<div class="history-title">' + escHtml(r.test_title || r.title || 'Test') + '</div>' +
        '<div class="history-meta"><span class="badge ' + gradeClass + '" style="margin-right:6px;font-weight:800;padding:2px 8px;border-radius:6px;font-size:11px;">' + grade + '</span> 📅 ' + date + ' • ✅ ' + r.correct_count + '/' + (r.total_count || 45) + '</div>' +
        '</div>' +
        '<div class="history-score"><div class="history-score-val" style="color:var(--primary);font-weight:800;">' + score + '</div><div class="history-score-sub">ball</div></div>' +
        '</div>';
    });
  }
  tab.innerHTML = html;
}

// ── PROFILE TAB ─────────────────────────────────
function renderProfileTab() {
  var tab = document.getElementById('tab-profile');
  var u = state.userInfo;
  var tgU = state.tgUser;
  var fullname = (u && u.fullname) || ((tgU && ((tgU.first_name || '') + ' ' + (tgU.last_name || '')).trim())) || 'Foydalanuvchi';
  var phone = (u && u.phone) || '\u2014';
  var username = (tgU && tgU.username) ? '@' + tgU.username : '\u2014';
  var tgId = (tgU && tgU.id) || 0;
  var testsCount = (u && u.tests_count) || 0;
  var avgScore = (u && u.avg_score) ? Math.round(u.avg_score) : 0;
  var maxScore = (u && u.max_score) || 0;
  var status = computeStatus(testsCount, avgScore);
  var avatarLetter = fullname.charAt(0).toUpperCase();

  tab.innerHTML =
    '<div class="profile-hero animate-in">' +
    '<div class="profile-avatar">' + avatarLetter + '</div>' +
    '<div class="profile-name">' + escHtml(fullname) + '</div>' +
    '<div class="profile-phone">' + escHtml(phone) + '</div>' +
    '<span class="profile-status-badge ' + status.cls + '">' + status.icon + ' ' + status.label + '</span>' +
    '</div>' +
    '<div class="stats-grid animate-in">' +
    '<div class="stat-card"><div class="stat-value">' + testsCount + '</div><div class="stat-label">' + t('stat_tests') + '</div></div>' +
    '<div class="stat-card"><div class="stat-value">' + avgScore + '</div><div class="stat-label">' + t('stat_avg') + '</div></div>' +
    '<div class="stat-card"><div class="stat-value">' + maxScore + '</div><div class="stat-label">' + t('stat_max') + '</div></div>' +
    '<div class="stat-card"><div class="stat-value">' + ((u && u.status === 'approved') ? '\u2705' : '\u23F3') + '</div><div class="stat-label">' + t('stat_status') + '</div></div>' +
    '</div>' +
    '<div class="card animate-in">' +
    '<div class="info-row"><div class="info-icon">\uD83D\uDC64</div><div><div class="info-label">' + t('info_name') + '</div><div class="info-value">' + escHtml(fullname) + '</div></div></div>' +
    '<div class="info-row"><div class="info-icon">\uD83D\uDCF1</div><div><div class="info-label">' + t('info_phone') + '</div><div class="info-value">' + escHtml(phone) + '</div></div></div>' +
    '<div class="info-row"><div class="info-icon">\uD83D\uDD17</div><div><div class="info-label">' + t('info_tg') + '</div><div class="info-value">' + escHtml(username) + '</div></div></div>' +
    '<div class="info-row"><div class="info-icon">\uD83C\uDD94</div><div><div class="info-label">' + t('info_id') + '</div><div class="info-value">' + tgId + '</div></div></div>' +
    '</div>' +
    '<button class="admin-action-btn" onclick="changePinPrompt()" style="margin-top:6px;">' +
    '<div class="btn-icon" style="background:rgba(248,113,113,0.12)">\uD83D\uDD11</div>' +
    '<span>' + t('change_pin') + '</span><span class="btn-arrow">\u203A</span></button>';
}

// ── ADMIN TAB ───────────────────────────────────
function renderAdminTab() {
  var tab = document.getElementById('tab-admin');
  tab.innerHTML =
    '<div class="admin-header-card animate-in">' +
    '<div class="admin-header-icon">\u2699\uFE0F</div>' +
    '<div><div style="font-size:16px;font-weight:800;color:var(--text)">' + t('admin_panel') + '</div>' +
    '<div style="font-size:12px;color:var(--text-muted);margin-top:2px">Tizimni boshqarish</div></div></div>' +
    '<div class="card animate-in" style="margin-top:12px">' +
    '<div style="font-size:13px;font-weight:700;color:var(--text);margin-bottom:12px">\uD83D\uDC65 ' + t('users_title') + '</div>' +
    '<div id="users-list"><div class="skeleton skeleton-card" style="height:50px"></div><div class="skeleton skeleton-card" style="height:50px;margin-top:8px"></div></div>' +
    '</div>';
}

function renderUsersSection(users, stats) {
  var listEl = document.getElementById('users-list');
  if (!listEl) return;
  if (!users || users.length === 0) {
    listEl.innerHTML = '<div class="empty-state"><div class="empty-icon">\uD83D\uDC65</div><p>' + t('users_title') + '</p></div>';
    return;
  }
  var statsHtml = '';
  if (stats) {
    statsHtml = '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:12px">' +
      '<div class="stat-card" style="padding:10px"><div class="stat-value" style="font-size:18px">' + (stats.total||0) + '</div><div class="stat-label">' + t('total') + '</div></div>' +
      '<div class="stat-card" style="padding:10px"><div class="stat-value" style="font-size:18px;color:var(--success)">' + (stats.approved||0) + '</div><div class="stat-label">' + t('approved') + '</div></div>' +
      '<div class="stat-card" style="padding:10px"><div class="stat-value" style="font-size:18px;color:var(--warning)">' + (stats.pending||0) + '</div><div class="stat-label">' + t('pending') + '</div></div>' +
      '</div>';
  }
  var usersHtml = users.slice(0, 30).map(function(u) {
    var letter = (u.fullname || 'F').charAt(0).toUpperCase();
    var tc = u.tests_count || 0;
    var sb = u.status === 'approved'
      ? '<span class="badge badge-active" style="padding:1px 6px;font-size:10px">\u2705</span>'
      : u.status === 'pending'
        ? '<span class="badge badge-pending" style="padding:1px 6px;font-size:10px">\u23F3</span>'
        : '<span class="badge badge-inactive" style="padding:1px 6px;font-size:10px">\uD83D\uDEAB</span>';
    return '<div class="user-row">' +
      '<div class="user-row-avatar">' + letter + '</div>' +
      '<div class="user-row-info">' +
      '<div class="user-row-name">' + escHtml(u.fullname || 'Nomaʼlum') + '</div>' +
      '<div class="user-row-meta">' + escHtml(u.phone || '\u2014') + ' \u2022 ' + tc + ' test</div>' +
      '</div>' + sb + '</div>';
  }).join('');
  if (users.length > 30) usersHtml += '<div style="text-align:center;font-size:12px;color:var(--text-muted);padding:8px">va yana ' + (users.length - 30) + ' ta...</div>';
  listEl.innerHTML = statsHtml + usersHtml;
}

// Webapp redirection functions removed (users will use bot inline buttons directly)

// ── PIN CHANGE ───────────────────────────────────
function changePinPrompt() {
  localStorage.removeItem(LS_PIN);
  state.pinBuffer = '';
  state.pinFirst = '';
  state.pinMode = 'setup';
  var pinScreen = document.getElementById('pin-screen');
  var app = document.getElementById('app');
  document.getElementById('pin-title').textContent = t('pin_create');
  document.getElementById('pin-subtitle').textContent = t('pin_create_sub');
  renderPinDots(0);
  showPinError('');
  app.style.display = 'none';
  app.classList.remove('visible');
  pinScreen.style.transition = '';
  pinScreen.style.opacity = '1';
  pinScreen.style.transform = 'scale(1)';
  pinScreen.style.display = 'flex';
}

// ── THEME ────────────────────────────────────────
function toggleTheme() {
  var cur = document.documentElement.getAttribute('data-theme') || 'dark';
  var next = cur === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem(LS_THEME, next);
  updateThemeIcon(next);
}

function updateThemeIcon(theme) {
  var el = document.getElementById('theme-icon');
  if (el) el.innerHTML = theme === 'dark' ? '&#9790;' : '&#9728;';
}

// ── LANGUAGE ─────────────────────────────────────
var LANGS = ['uz', 'ru', 'en'];
var LANG_LABELS = { uz: 'UZ', ru: 'RU', en: 'EN' };

function cycleLang() {
  var cur = localStorage.getItem(LS_LANG) || 'uz';
  var idx = LANGS.indexOf(cur);
  var next = LANGS[(idx + 1) % LANGS.length];
  localStorage.setItem(LS_LANG, next);
  updateLangLabel();
  applyI18n();
  // Aktiv tabni qayta render qilish
  if (state.activeTab) switchTab(state.activeTab);
}

function updateLangLabel() {
  var cur = localStorage.getItem(LS_LANG) || 'uz';
  var el = document.getElementById('lang-label');
  if (el) el.textContent = LANG_LABELS[cur] || 'UZ';
}

function applyI18n() {
  // data-i18n atributli barcha elementlar
  document.querySelectorAll('[data-i18n]').forEach(function(el) {
    el.textContent = t(el.getAttribute('data-i18n'));
  });
  // PIN ekrani matnlari
  var pinTitle = document.getElementById('pin-title');
  var pinSub = document.getElementById('pin-subtitle');
  if (pinTitle && pinSub) {
    var hasPin = !!localStorage.getItem(LS_PIN);
    if (!hasPin || state.pinMode === 'setup') {
      pinTitle.textContent = t('pin_create');
      pinSub.textContent = t('pin_create_sub');
    } else {
      pinSub.textContent = t('pin_enter_sub');
    }
  }
}

// ── RESULT MODAL ─────────────────────────────────
function showResultModal(result) {
  var modal = document.getElementById('result-modal');
  var title = document.getElementById('result-modal-title');
  var body = document.getElementById('result-modal-body');
  if (!modal || !body) return;

  var score = (result.score != null) ? result.score : 0;
  var maxScore = result.max_score || 100;
  var grade = result.grade || getGradeFromScore(score, maxScore);
  var gradeClass = gradeToClass(grade);
  var date = formatDate(result.submitted_at);
  var correct = result.correct_count || 0;
  var total = result.total_count || 45;
  var wrong = result.incorrect_count || (total - correct);
  var blank = result.unanswered_count || 0;

  var gradeBg = { 'grade-5':'rgba(16,185,129,0.15)', 'grade-4':'rgba(59,130,246,0.15)', 'grade-3':'rgba(245,158,11,0.15)', 'grade-2':'rgba(239,68,68,0.15)' };
  var gradeColor = { 'grade-5':'#10B981', 'grade-4':'#3B82F6', 'grade-3':'#F59E0B', 'grade-2':'#EF4444' };
  var gradeBorder = { 'grade-5':'#10B981', 'grade-4':'#3B82F6', 'grade-3':'#F59E0B', 'grade-2':'#EF4444' };

  title.textContent = (result.test_title || result.title || 'Test Natijasi');
  body.innerHTML =
    '<div style="text-align:center;margin:10px 0 16px;">' +
      '<div style="display:inline-flex;flex-direction:column;align-items:center;justify-content:center;padding:12px 28px;border-radius:18px;background:' + (gradeBg[gradeClass]||'rgba(99,102,241,0.15)') + ';border:2px solid ' + (gradeBorder[gradeClass]||'#6366F1') + ';min-width:140px;">' +
        '<span style="font-size:32px;font-weight:900;line-height:1.1;color:' + (gradeColor[gradeClass]||'#6366F1') + ';">' + grade + '</span>' +
        '<span style="font-size:14px;font-weight:800;color:var(--text-main);margin-top:4px;">' + score + ' ball</span>' +
      '</div>' +
    '</div>' +
    '<div id="compare-keys-section" style="text-align:center; margin: 12px 0;">' +
      '<button id="btn-compare-keys" onclick="promptCompareKeys(' + result.test_id + ')" style="background:linear-gradient(135deg, #3B82F6, #6366F1);color:white;border:none;padding:12px;border-radius:12px;font-weight:800;font-size:14.5px;cursor:pointer;width:100%;box-shadow:0 4px 14px rgba(59, 130, 246, 0.4);">🔑 To\'g\'ri javoblarni ko\'rish</button>' +
      '<div id="compare-keys-auth" style="display:none;margin-top:10px;background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:12px;">' +
        '<p style="font-size:12px;color:var(--text-muted);margin-bottom:8px;font-weight:600;">Test kalitlarini ko\'rish uchun maxfiy parolni kiriting</p>' +
        '<input type="password" id="input-key-code" placeholder="Parol..." style="width:100%;padding:10px;border-radius:8px;border:1px solid var(--border);background:var(--bg-body);color:var(--text-main);font-size:14px;margin-bottom:8px;">' +
        '<button onclick="submitCompareKeys(' + result.test_id + ')" style="background:#10B981;color:white;border:none;padding:10px;border-radius:8px;font-weight:700;cursor:pointer;width:100%;">Tasdiqlash</button>' +
        '<div id="compare-keys-error" style="color:var(--error);font-size:12px;margin-top:6px;display:none;"></div>' +
      '</div>' +
    '</div>' +
    '<div id="compare-keys-result" style="display:none;margin-bottom:16px;max-height:250px;overflow-y:auto;border:1px solid var(--border);border-radius:12px;padding:8px;"></div>' +
    '<div class="result-row"><span class="result-row-label">To\'plangan ball</span><span class="result-row-val" style="color:var(--primary);font-weight:800;font-size:16px;">' + score + ' ball</span></div>' +
    '<div class="result-row"><span class="result-row-label">' + t('result_grade') + '</span><span class="result-row-val" style="color:' + (gradeColor[gradeClass]||'var(--accent)') + ';font-weight:800;">' + grade + '</span></div>' +
    '<div class="result-row"><span class="result-row-label">' + t('result_correct') + '</span><span class="result-row-val green">' + correct + ' / ' + total + ' ta</span></div>' +
    '<div class="result-row"><span class="result-row-label">' + t('result_wrong') + '</span><span class="result-row-val red">' + wrong + ' ta</span></div>' +
    '<div class="result-row"><span class="result-row-label">' + t('result_blank') + '</span><span class="result-row-val orange">' + blank + ' ta</span></div>' +
    '<div class="result-row"><span class="result-row-label">' + t('result_date') + '</span><span class="result-row-val">' + date + '</span></div>';

  modal.style.display = 'flex';
}

function promptCompareKeys(testId) {
  document.getElementById('btn-compare-keys').style.display = 'none';
  document.getElementById('compare-keys-auth').style.display = 'block';
}

async function submitCompareKeys(testId) {
  var tgId = (state.tgUser && state.tgUser.id) || 0;
  var code = document.getElementById('input-key-code').value.trim();
  var errEl = document.getElementById('compare-keys-error');
  var resEl = document.getElementById('compare-keys-result');
  
  if (!code) {
    errEl.textContent = "Iltimos, parolni kiriting!";
    errEl.style.display = 'block';
    return;
  }
  
  try {
    const res = await fetch('/api/app/compare-keys', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tg_id: tgId, test_id: testId, code: code })
    });
    const data = await res.json();
    
    if (data.success) {
      document.getElementById('compare-keys-auth').style.display = 'none';
      renderKeyComparison(data.correct_answers, data.user_answers, resEl);
    } else {
      errEl.textContent = data.message || "Xatolik yuz berdi.";
      errEl.style.display = 'block';
    }
  } catch(e) {
    errEl.textContent = "Tarmoq xatosi.";
    errEl.style.display = 'block';
  }
}

function renderKeyComparison(correct, user, container) {
  container.style.display = 'block';
  var html = '<h4 style="margin:0 0 8px;font-size:14px;">Kalitlar solishtiruvi</h4>';
  html += '<div style="display:grid;grid-template-columns:repeat(auto-fill, minmax(60px, 1fr));gap:6px;">';
  
  for (var i = 1; i <= 45; i++) {
    // Handling open questions like 36a, 36b
    var isMultiple = (i >= 36);
    if (isMultiple) {
      ['a', 'b'].forEach(function(sub) {
        var key = i + sub;
        var cVal = correct[key] ? correct[key].ans : '-';
        var uVal = user[key] || '-';
        var isOk = (cVal === uVal);
        var bg = isOk ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)';
        var col = isOk ? '#10B981' : '#EF4444';
        
        html += '<div style="background:'+bg+';color:'+col+';border:1px solid '+col+';border-radius:6px;padding:4px;text-align:center;font-size:11px;">';
        html += '<b>' + key + '</b><br>' + uVal + ' / ' + cVal;
        html += '</div>';
      });
    } else {
      var key = String(i);
      var cVal = correct[key] ? correct[key].ans : '-';
      var uVal = user[key] || '-';
      var isOk = (cVal === uVal);
      var bg = isOk ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)';
      var col = isOk ? '#10B981' : '#EF4444';
      
      html += '<div style="background:'+bg+';color:'+col+';border:1px solid '+col+';border-radius:6px;padding:4px;text-align:center;font-size:11px;">';
      html += '<b>' + key + '</b><br>' + uVal + ' / ' + cVal;
      html += '</div>';
    }
  }
  
  html += '</div>';
  container.innerHTML = html;

}

function closeResultModal(e) {
  if (e && e.target && e.target.id !== 'result-modal') return;
  var modal = document.getElementById('result-modal');
  if (modal) modal.style.display = 'none';
}

// ── HEADER UPDATE ────────────────────────────────
function updateHeaderUser() {
  var u = state.userInfo;
  var tgU = state.tgUser;
  var name = (u && u.fullname) || (tgU && tgU.first_name) || 'F';
  var el = document.getElementById('header-avatar');
  if (el) el.textContent = name.charAt(0).toUpperCase();
}

// ── HELPERS ─────────────────────────────────────
function computeStatus(testsCount, avgScore) {
  if (testsCount === 0) return { label: t('status_new'), icon: '\uD83C\uDF31', cls: 'status-beginner' };
  if (avgScore >= 40) return { label: t('status_gold'), icon: '\uD83E\uDD47', cls: 'status-gold' };
  if (avgScore >= 30) return { label: t('status_silver'), icon: '\uD83E\uDD48', cls: 'status-silver' };
  if (avgScore >= 20) return { label: t('status_bronze'), icon: '\uD83E\uDD49', cls: 'status-bronze' };
  return { label: t('status_learner'), icon: '\uD83D\uDCDA', cls: 'status-beginner' };
}

function getGradeFromScore(score, maxScore) {
  var s = parseFloat(score) || 0;
  var max = parseFloat(maxScore) || 100;
  var pct = (max > 0) ? (s / max * 100) : s;
  
  if (pct >= 86 || s >= 70) return 'A+';
  if (pct >= 75 || s >= 65) return 'A';
  if (pct >= 65 || s >= 60) return 'B+';
  if (pct >= 60 || s >= 55) return 'B';
  if (pct >= 55 || s >= 50) return 'C+';
  if (pct >= 46 || s >= 46) return 'C';
  return 'Yetarli emas';
}

function gradeToClass(grade) {
  if (!grade) return 'grade-2';
  var g = String(grade).toUpperCase();
  if (g.startsWith('A')) return 'grade-5';
  if (g.startsWith('B')) return 'grade-4';
  if (g.startsWith('C')) return 'grade-3';
  return 'grade-2';
}

function formatDate(ts) {
  if (!ts) return '\u2014';
  var d = new Date(ts * 1000);
  return d.toLocaleDateString('uz-UZ', { day:'2-digit', month:'2-digit', year:'numeric' }) +
    ' ' + d.toLocaleTimeString('uz-UZ', { hour:'2-digit', minute:'2-digit' });
}

function escHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function showToast(msg) {
  var toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(function() { toast.classList.remove('show'); }, 2200);
}
