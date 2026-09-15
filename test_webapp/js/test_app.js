/**
 * Test Tekshirish Tizimi — Asosiy Mini App Mantiqi
 */

const TestApp = {
  testId: 1,
  testCode: 'TEST-01',
  testTitle: 'Matematika Blok Test',
  subject: 'Matematika',
  userTgId: 0,
  userFullname: 'Foydalanuvchi',
  isDarkMode: false,

  // Foydalanuvchi belgilagan javoblar
  answers: {},

  init() {
    if (window.BM_LOGO_B64) {
      document.querySelectorAll('.intro-logo-img, .header-bm-logo').forEach(img => {
        img.src = window.BM_LOGO_B64;
      });
    }

    // 1. Telegram WebApp ni sozlash
    if (window.Telegram && window.Telegram.WebApp) {
      const tg = window.Telegram.WebApp;
      tg.ready();
      tg.expand();

      // Foydalanuvchi ma'lumotlari
      if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
        const u = tg.initDataUnsafe.user;
        this.userTgId = u.id;
        this.userFullname = `${u.first_name || ''} ${u.last_name || ''}`.trim() || u.username || 'Foydalanuvchi';
      }

      // Mavzu
      if (tg.colorScheme === 'dark') {
        this.setTheme(true);
      }
    }

    // 2. URL parametrlardan test ma'lumotlarini olish
    const params = new URLSearchParams(window.location.search);
    if (params.has('test_code')) this.testCode = params.get('test_code');
    if (params.has('test_id')) this.testId = parseInt(params.get('test_id')) || 1;
    if (params.has('title')) this.testTitle = params.get('title');
    if (params.has('subject')) this.subject = params.get('subject');
    if (params.has('user_id')) this.userTgId = parseInt(params.get('user_id')) || this.userTgId;
    if (params.has('name')) this.userFullname = params.get('name');

    // UI ga o'rnatish
    const titleEl = document.getElementById('test-title-display');
    const codeEl = document.getElementById('test-code-display');
    const subjectEl = document.getElementById('test-subject-badge');
    const userEl = document.getElementById('user-welcome-text');

    if (titleEl) titleEl.textContent = this.testTitle;
    if (codeEl) codeEl.textContent = `KOD: #${this.testCode}`;
    if (subjectEl) subjectEl.textContent = `📐 ${this.subject}`;
    if (userEl) userEl.textContent = `Ishtirokchi: ${this.userFullname}`;

    // 3. Savollarni render qilish
    this.renderQuestions();
    this.renderMapGrid();
    this.updateProgress();

    // 4. Mavzuga mos kirish animatsiyasini ishga tushirish
    this.runIntroAnimation();
  },

  runIntroAnimation() {
    const splash = document.getElementById('intro-splash');
    if (!splash) return;

    const codeEl = document.getElementById('intro-test-code');
    const userEl = document.getElementById('intro-user-name');
    const barEl = document.getElementById('intro-loader-bar');
    const statusEl = document.getElementById('intro-loading-status');

    if (codeEl) codeEl.textContent = `KOD: #${this.testCode}`;
    if (userEl) userEl.innerHTML = `Ishtirokchi: <strong>${this.userFullname}</strong>`;

    setTimeout(() => {
      if (barEl) barEl.style.width = '35%';
      if (statusEl) statusEl.innerHTML = '<span>📐 Matematik modul tayyorlanmoqda...</span>';
    }, 150);

    setTimeout(() => {
      if (barEl) barEl.style.width = '75%';
      if (statusEl) statusEl.innerHTML = '<span>⚡ 45 ta savol va formulalar yuklandi...</span>';
    }, 600);

    setTimeout(() => {
      if (barEl) barEl.style.width = '100%';
      if (statusEl) statusEl.innerHTML = '<span>🚀 Boshladik! Omad tilaymiz!</span>';
    }, 1050);

    setTimeout(() => {
      splash.classList.add('fade-out');
      setTimeout(() => {
        splash.style.display = 'none';
      }, 600);
    }, 1450);
  },

  toggleTheme() {
    this.setTheme(!this.isDarkMode);
  },

  setTheme(isDark) {
    this.isDarkMode = isDark;
    document.body.classList.toggle('dark-mode', isDark);
  },

  // ----------------------------------------------------
  // SAVOLLARNI GENERATSIYA QILISH
  // ----------------------------------------------------
  renderQuestions() {
    const part1 = document.getElementById('questions-part-1');
    const part2 = document.getElementById('questions-part-2');
    const part3 = document.getElementById('questions-part-3');

    // 1. 1-32 Variantli Savollar (A, B, C, D)
    if (part1) {
      let html1 = '';
      for (let q = 1; q <= 32; q++) {
        html1 += `
          <div class="question-card" id="qcard-${q}">
            <span class="question-num-tag">${q}-savol</span>
            <div class="options-group">
              ${['A', 'B', 'C', 'D'].map(opt => `
                <button class="option-btn" id="opt-${q}-${opt}" onclick="TestApp.selectOption(${q}, '${opt}')">
                  ${opt}
                </button>
              `).join('')}
            </div>
          </div>
        `;
      }
      part1.innerHTML = html1;
    }

    // 2. 33, 34, 35 savollar: 6 ta variantli (A, B, C, D, E, F)
    if (part2) {
      let html2 = '';
      for (let q = 33; q <= 35; q++) {
        html2 += `
          <div class="question-card" id="qcard-${q}" style="flex-direction: column; align-items: flex-start; gap: 8px; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; width: 100%;">
              <span class="question-num-tag" style="font-size: 13.5px; font-weight: 800;">${q}-savol (6 ta variant)</span>
              <span style="font-size: 11px; color: var(--text-muted);">Maxsus savol</span>
            </div>
            <div class="options-group-6" style="width: 100%;">
              ${['A', 'B', 'C', 'D', 'E', 'F'].map(opt => `
                <button class="option-btn" id="opt-${q}-${opt}" onclick="TestApp.selectOption(${q}, '${opt}')">
                  ${opt}
                </button>
              `).join('')}
            </div>
          </div>
        `;
      }
      part2.innerHTML = html2;
    }

    // 3. 36-45 Yopiq Savollar (a va b qismlar alohida qator shaklida)
    if (part3) {
      let html3 = '';
      for (let q = 36; q <= 45; q++) {
        for (let sub of ['a', 'b']) {
          const key = `${q}${sub}`;
          html3 += `
            <div class="open-question-row" id="qrow-${key}">
              <div class="savol-badge">${key}-savol</div>
              <div class="savol-input-box" id="box-${key}" onclick="MathKeyboard.openFor('${key}')">
                <input type="text" class="savol-input" id="input-${key}" readonly placeholder="" onclick="MathKeyboard.openFor('${key}')">
              </div>
              <button type="button" class="btn-kb-icon" onclick="MathKeyboard.openFor('${key}')" title="Klaviaturani ochish">⌨️</button>
            </div>
          `;
        }
      }
      part3.innerHTML = html3;
    }
  },

  // ----------------------------------------------------
  // JAVOBNI TANLASH VA O'RNATISH
  // ----------------------------------------------------
  selectOption(qNum, option) {
    const key = String(qNum);
    const prev = this.answers[key];

    // Variant tugmalarini yangilash (33, 34, 35 savollar 6 ta variant: A, B, C, D, E, F)
    const opts = [33, 34, 35].includes(qNum) ? ['A', 'B', 'C', 'D', 'E', 'F'] : ['A', 'B', 'C', 'D'];
    opts.forEach(opt => {
      const btn = document.getElementById(`opt-${qNum}-${opt}`);
      if (btn) btn.classList.toggle('selected', opt === option);
    });

    this.answers[key] = option;

    const card = document.getElementById(`qcard-${qNum}`);
    if (card) card.classList.add('answered');

    if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.HapticFeedback) {
      window.Telegram.WebApp.HapticFeedback.impactOccurred('light');
    }

    this.updateProgress();
    this.updateMapItem(String(qNum), true);
  },

  setOpenAnswer(fieldKey, val) {
    this.answers[fieldKey] = val;

    const box = document.getElementById(`box-${fieldKey}`);
    if (box) {
      box.classList.toggle('filled', (val || '').trim().length > 0);
    }

    const isFilled = (val || '').trim().length > 0;
    this.updateMapItem(fieldKey, isFilled);
    this.updateProgress();
  },

  // ----------------------------------------------------
  // PROGRESS VA XARITA (JAMI 55 TA SAVOL: 1-35 VA 36a-45b)
  // ----------------------------------------------------
  renderMapGrid() {
    const grid = document.getElementById('map-grid');
    if (!grid) return;

    let html = '';
    // 1-35 savollar
    for (let q = 1; q <= 35; q++) {
      html += `
        <button class="map-num-btn" id="map-btn-${q}" onclick="TestApp.scrollToQuestion('${q}')">
          ${q}
        </button>
      `;
    }
    // 36a dan 45b gacha (20 ta alohida savol)
    for (let q = 36; q <= 45; q++) {
      for (let sub of ['a', 'b']) {
        const key = `${q}${sub}`;
        html += `
          <button class="map-num-btn open-map-btn" id="map-btn-${key}" onclick="TestApp.scrollToQuestion('${key}')" style="font-size: 11.5px; font-weight: 800; min-width: 36px; padding: 4px 2px;">
            ${key}
          </button>
        `;
      }
    }
    grid.innerHTML = html;
  },

  toggleNavMap() {
    const map = document.getElementById('questions-nav-map');
    const arrow = document.getElementById('map-arrow-icon');
    if (!map) return;

    const isOpen = map.style.display !== 'none';
    map.style.display = isOpen ? 'none' : 'block';
    if (arrow) arrow.textContent = isOpen ? '▼' : '▲';
  },

  scrollToQuestion(key) {
    const el = document.getElementById(`qcard-${key}`) || document.getElementById(`qrow-${key}`);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      el.classList.add('pulse-highlight');
      setTimeout(() => el.classList.remove('pulse-highlight'), 1200);
    }
    this.toggleNavMap();
  },

  updateMapItem(key, isFilled) {
    const btn = document.getElementById(`map-btn-${key}`);
    if (btn) btn.classList.toggle('answered', isFilled);
  },

  updateProgress() {
    let answeredQuestions = 0;

    // 1-35 savollar (35 ta)
    for (let q = 1; q <= 35; q++) {
      if (this.answers[String(q)]) answeredQuestions++;
    }

    // 36a-45b savollar (20 ta alohida savol)
    for (let q = 36; q <= 45; q++) {
      for (let sub of ['a', 'b']) {
        const key = `${q}${sub}`;
        const input = document.getElementById(`input-${key}`);
        const val = this.answers[key] !== undefined ? this.answers[key] : (input ? input.value : '');
        if ((val || '').trim().length > 0) {
          answeredQuestions++;
        }
      }
    }

    const total = 55;
    const remaining = total - answeredQuestions;
    const percent = Math.round((answeredQuestions / total) * 100);

    const countEl = document.getElementById('answered-counter');
    const fillEl = document.getElementById('progress-bar-fill');
    const dockText = document.getElementById('dock-answered-text');
    const dockSub = document.getElementById('dock-unanswered-text');

    if (countEl) countEl.textContent = `${answeredQuestions} / ${total}`;
    if (fillEl) fillEl.style.width = `${percent}%`;
    if (dockText) dockText.textContent = `${answeredQuestions} / ${total} ta belgilandi (${percent}%)`;
    if (dockSub) dockSub.textContent = remaining === 0 ? '🎉 Barcha 55 ta savol to\'ldirildi!' : `${remaining} ta savol qoldi`;
  },

  // ----------------------------------------------------
  // TESTNI TOPSHIRISH (SUBMIT)
  // ----------------------------------------------------
  openConfirmSubmitModal() {
    if (typeof MathKeyboard !== 'undefined' && MathKeyboard.close) {
      MathKeyboard.close();
    }
    
    // Barcha ochiq savol inputlarini sinxronlashtirish
    for (let q = 36; q <= 45; q++) {
      for (let sub of ['a', 'b']) {
        const key = `${q}${sub}`;
        const input = document.getElementById(`input-${key}`);
        if (input && input.value !== undefined) {
          this.answers[key] = input.value.trim();
        }
      }
    }

    let answered = 0;
    for (let q = 1; q <= 35; q++) {
      if (this.answers[String(q)]) answered++;
    }
    for (let q = 36; q <= 45; q++) {
      for (let sub of ['a', 'b']) {
        const key = `${q}${sub}`;
        if ((this.answers[key] || '').trim().length > 0) {
          answered++;
        }
      }
    }

    const total = 55;
    const empty = total - answered;

    const mAnswered = document.getElementById('m-stat-answered');
    const mEmpty = document.getElementById('m-stat-empty');

    if (mAnswered) mAnswered.textContent = answered;
    if (mEmpty) mEmpty.textContent = empty;

    const modal = document.getElementById('confirm-modal');
    if (modal) modal.classList.add('open');
  },

  closeConfirmSubmitModal() {
    const modal = document.getElementById('confirm-modal');
    if (modal) modal.classList.remove('open');
  },

  async submitTestNow() {
    const submitBtn = document.getElementById('btn-final-submit');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Tekshirilmoqda... ⏳';
    }

    // 36a-45b savollar qiymatlarini to'g'ridan-to'g'ri DOM dan olib yakuniy tekshirish
    for (let q = 36; q <= 45; q++) {
      for (let sub of ['a', 'b']) {
        const key = `${q}${sub}`;
        const input = document.getElementById(`input-${key}`);
        if (input && input.value !== undefined) {
          this.answers[key] = input.value.trim();
        }
      }
    }

    const payload = {
      test_id: this.testId,
      test_code: this.testCode,
      user_tg_id: this.userTgId,
      fullname: this.userFullname,
      answers: this.answers
    };

    try {
      const response = await fetch('/api/submit-test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const result = await response.json();
      this.closeConfirmSubmitModal();

      if (result.success && result.data) {
        this.showResultModal(result.data);
      } else {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Testni yakunlash';
        }
        if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.showAlert) {
          window.Telegram.WebApp.showAlert(result.message || 'Javoblarni yuborishda xatolik!');
        } else {
          alert(result.message || 'Javoblarni yuborishda xatolik yuz berdi!');
        }
      }
    } catch (e) {
      console.error('Submit error:', e);
      this.closeConfirmSubmitModal();
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Testni yakunlash';
      }
      alert('Tarmoq xatoligi yoki serverga ulanishda muammo yuz berdi. Iltimos, qayta urinib ko\'ring.');
    }
  },

  showResultModal(data) {
    const modal = document.getElementById('result-modal');
    if (!modal) return;

    const nameEl = document.getElementById('result-user-name');
    const scoreNum = document.getElementById('result-score-num');
    const correctEl = document.getElementById('r-correct-count');
    const incorrectEl = document.getElementById('r-incorrect-count');
    const emptyEl = document.getElementById('r-unanswered-count');

    if (nameEl) nameEl.textContent = data.fullname || this.userFullname;
    
    // Real statistika raqamlarini o'rnatish
    if (correctEl) correctEl.textContent = `${data.correct_count ?? 0} ta`;
    if (incorrectEl) incorrectEl.textContent = `${data.incorrect_count ?? 0} ta`;
    if (emptyEl) emptyEl.textContent = `${data.unanswered_count ?? 0} ta`;

    // Milliy sertifikat darajasi va to'plangan ball
    const gradeVal = document.getElementById('result-grade-val');
    if (gradeVal) {
      const grade = data.grade || '—';
      const score = (data.score !== undefined && data.score !== null) ? `${data.score} ball` : '';
      gradeVal.textContent = `${grade} ${score ? `(${score})` : ''}`;
    }

    this.lastResultData = data;
    modal.classList.add('open');

    if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.HapticFeedback) {
      window.Telegram.WebApp.HapticFeedback.notificationOccurred('success');
    }
  },

  openAnswersAnalysis() {
    const data = this.lastResultData;
    if (!data || !data.details) return;

    const container = document.getElementById('analysis-items-container');
    if (!container) return;

    let html = '';
    const details = data.details;

    Object.keys(details).forEach(key => {
      const item = details[key];
      const isCorrect = item.status === 'correct';
      const isUnanswered = item.status === 'unanswered';
      
      let statusBg = isCorrect ? 'rgba(16, 185, 129, 0.12)' : (isUnanswered ? 'rgba(100, 116, 139, 0.12)' : 'rgba(239, 68, 68, 0.12)');
      let statusBorder = isCorrect ? '#10B981' : (isUnanswered ? '#94A3B8' : '#EF4444');
      let statusIcon = isCorrect ? '✅' : (isUnanswered ? '⚪️' : '❌');
      let statusLabel = isCorrect ? 'To\'g\'ri' : (isUnanswered ? 'Belgilanmagan' : 'Noto\'g\'ri');

      let userAnsDisplay = (item.user || '').trim() || '<span style="color: #94A3B8; font-style: italic;">(Belgilanmadi)</span>';
      let correctAnsDisplay = item.correct || '—';

      html += `
        <div style="background: ${statusBg}; border: 1px solid ${statusBorder}; border-radius: 10px; padding: 10px 12px; display: flex; flex-direction: column; gap: 6px;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight: 800; font-size: 13.5px; color: var(--text-main);">${item.num || key + '-savol'}</span>
            <span style="font-size: 12px; font-weight: 800; display: inline-flex; align-items: center; gap: 4px;">${statusIcon} ${statusLabel}</span>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 13px; margin-top: 2px;">
            <span>Sizning javobingiz: <strong>${userAnsDisplay}</strong></span>
            <span style="color: #10B981;">To'g'ri kalit: <strong>${correctAnsDisplay}</strong></span>
          </div>
        </div>
      `;
    });

    container.innerHTML = html;
    const modal = document.getElementById('analysis-modal');
    if (modal) modal.classList.add('open');
  },

  closeAnswersAnalysis() {
    const modal = document.getElementById('analysis-modal');
    if (modal) modal.classList.remove('open');
  },

  closeWebApp() {
    if (window.Telegram && window.Telegram.WebApp) {
      window.Telegram.WebApp.close();
    } else {
      window.location.reload();
    }
  }
};

window.TestApp = TestApp;

document.addEventListener('DOMContentLoaded', () => {
  TestApp.init();
});
