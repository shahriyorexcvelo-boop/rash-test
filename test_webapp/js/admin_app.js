/**
 * Admin Test & Key Creator Controller
 */
const AdminApp = {
  answers: {}, // {"1": {"ans": "", "score": 2.0}, ...}

  init() {
    if (window.Telegram && window.Telegram.WebApp) {
      window.Telegram.WebApp.ready();
      window.Telegram.WebApp.expand();
    }

    this.initAnswers();
    this.renderForm();
    this.recalculateTotal();
    this.updateUnfilledStats();
    this.runIntroAnimation();
  },

  runIntroAnimation() {
    // Mini ilovani darhol bir zumda ochish (hech qanday sun'iy kutishlarsiz)
    const splash = document.getElementById('intro-splash');
    if (splash) {
      splash.style.display = 'none';
    }
  },

  initAnswers() {
    // 1-32 (2.0 ball dan, 4 ta variant) - boshlang'ichda bo'sh
    for (let q = 1; q <= 32; q++) {
      this.answers[String(q)] = { ans: '', score: 2.0 };
    }
    // 33, 34, 35 (2.0 ball dan, 6 ta variant: A-F) - boshlang'ichda bo'sh
    for (let q = 33; q <= 35; q++) {
      this.answers[String(q)] = { ans: '', score: 2.0 };
    }
    // 36a-45b (1.5 ball dan, yozma/ochiq javob) - boshlang'ichda bo'sh
    for (let q = 36; q <= 45; q++) {
      this.answers[`${q}a`] = { ans: '', score: 1.5 };
      this.answers[`${q}b`] = { ans: '', score: 1.5 };
    }
  },

  renderForm() {
    const part1 = document.getElementById('admin-part-1');
    const part2 = document.getElementById('admin-part-2');
    const part3 = document.getElementById('admin-part-3');

    // 1. 1-32 savollar (A, B, C, D)
    if (part1) {
      let html = '';
      for (let q = 1; q <= 32; q++) {
        const curAns = this.answers[String(q)].ans;
        const curScore = this.answers[String(q)].score;
        html += `
          <div class="q-admin-row">
            <span class="q-admin-num">${q}.</span>
            <div class="options-group" style="flex: 1;">
              ${['A', 'B', 'C', 'D'].map(opt => `
                <button class="option-btn ${opt === curAns ? 'selected' : ''}" id="adm-opt-${q}-${opt}" onclick="AdminApp.selectChoice(${q}, '${opt}')">
                  ${opt}
                </button>
              `).join('')}
            </div>
            <div class="score-input-wrap">
              <input type="number" step="0.5" min="0" class="score-input" id="score-${q}" value="${curScore}" onchange="AdminApp.updateScore('${q}', this.value)">
              <span class="score-unit">ball</span>
            </div>
          </div>
        `;
      }
      part1.innerHTML = html;
    }

    // 2. 33, 34, 35 savollar (6 ta variant: A, B, C, D, E, F)
    if (part2) {
      let html = '';
      for (let q = 33; q <= 35; q++) {
        const curAns = this.answers[String(q)].ans;
        const curScore = this.answers[String(q)].score;
        html += `
          <div class="q-admin-row" style="flex-direction: column; align-items: stretch; gap: 8px; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span class="q-admin-num" style="font-weight: 800;">${q}-savol (6 ta variant)</span>
              <div class="score-input-wrap">
                <input type="number" step="0.5" min="0" class="score-input" id="score-${q}" value="${curScore}" onchange="AdminApp.updateScore('${q}', this.value)">
                <span class="score-unit">ball</span>
              </div>
            </div>
            <div class="options-group-6">
              ${['A', 'B', 'C', 'D', 'E', 'F'].map(opt => `
                <button class="option-btn ${opt === curAns ? 'selected' : ''}" id="adm-opt-${q}-${opt}" onclick="AdminApp.selectChoice(${q}, '${opt}')">
                  ${opt}
                </button>
              `).join('')}
            </div>
          </div>
        `;
      }
      part2.innerHTML = html;
    }

    // 3. 36-45
    if (part3) {
      let html = '';
      for (let q = 36; q <= 45; q++) {
        const itemA = this.answers[`${q}a`];
        const itemB = this.answers[`${q}b`];
        html += `
          <div class="open-admin-box">
            <span style="font-size: 13px; font-weight: 800;">${q}-savol (Yopiq yozma)</span>
            
            <!-- a -->
            <div class="open-admin-sub-row">
              <span style="font-size: 12px; font-weight: 800; color: var(--primary); min-width: 28px;">${q}a:</span>
              <div class="savol-input-box" id="box-${q}a" onclick="MathKeyboard.openFor('${q}a')" style="height: 38px; flex: 1; padding: 0 8px; cursor: pointer;">
                <input type="text" class="savol-input" id="input-${q}a" readonly placeholder="Kalitni klaviaturadan kiriting" value="${itemA.ans}" onclick="MathKeyboard.openFor('${q}a')" style="font-size: 13px; cursor: pointer;">
              </div>
              <button type="button" class="btn-kb-icon" style="width: 36px; height: 38px; font-size: 16px; border-radius: 10px;" onclick="MathKeyboard.openFor('${q}a')" title="Matematik klaviatura">⌨️</button>
              <div class="score-input-wrap">
                <input type="number" step="0.5" min="0" class="score-input" value="${itemA.score}" onchange="AdminApp.updateScore('${q}a', this.value)">
                <span class="score-unit">ball</span>
              </div>
            </div>

            <!-- b -->
            <div class="open-admin-sub-row">
              <span style="font-size: 12px; font-weight: 800; color: var(--primary); min-width: 28px;">${q}b:</span>
              <div class="savol-input-box" id="box-${q}b" onclick="MathKeyboard.openFor('${q}b')" style="height: 38px; flex: 1; padding: 0 8px; cursor: pointer;">
                <input type="text" class="savol-input" id="input-${q}b" readonly placeholder="Kalitni klaviaturadan kiriting" value="${itemB.ans}" onclick="MathKeyboard.openFor('${q}b')" style="font-size: 13px; cursor: pointer;">
              </div>
              <button type="button" class="btn-kb-icon" style="width: 36px; height: 38px; font-size: 16px; border-radius: 10px;" onclick="MathKeyboard.openFor('${q}b')" title="Matematik klaviatura">⌨️</button>
              <div class="score-input-wrap">
                <input type="number" step="0.5" min="0" class="score-input" value="${itemB.score}" onchange="AdminApp.updateScore('${q}b', this.value)">
                <span class="score-unit">ball</span>
              </div>
            </div>
          </div>
        `;
      }
      part3.innerHTML = html;
    }
  },

  selectChoice(qNum, option) {
    const key = String(qNum);
    this.answers[key].ans = option;

    const opts = [33, 34, 35].includes(qNum) ? ['A', 'B', 'C', 'D', 'E', 'F'] : ['A', 'B', 'C', 'D'];
    opts.forEach(opt => {
      const btn = document.getElementById(`adm-opt-${qNum}-${opt}`);
      if (btn) btn.classList.toggle('selected', opt === option);
    });

    this.updateUnfilledStats();

    if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.HapticFeedback) {
      window.Telegram.WebApp.HapticFeedback.impactOccurred('light');
    }
  },

  updateScore(key, val) {
    const num = parseFloat(val) || 0.0;
    if (this.answers[key]) {
      this.answers[key].score = num;
    }
    this.recalculateTotal();
  },

  updateOpenAns(key, val) {
    if (this.answers[key]) {
      this.answers[key].ans = val;
    }
    const input = document.getElementById(`input-${key}`);
    if (input && input.value !== val) {
      input.value = val;
    }
    const box = document.getElementById(`box-${key}`);
    if (box) {
      box.classList.toggle('filled', (val || '').trim().length > 0);
    }
    this.updateUnfilledStats();
  },

  recalculateTotal() {
    let total = 0.0;
    Object.values(this.answers).forEach(item => {
      total += (parseFloat(item.score) || 0.0);
    });
    total = Math.round(total * 10) / 10;

    const badge = document.getElementById('admin-total-badge');
    const dock = document.getElementById('admin-dock-total');

    if (badge) badge.textContent = `🎯 Jami: ${total} ball`;
    if (dock) dock.textContent = `Jami: ${total} ball`;
  },

  updateUnfilledStats() {
    let closedUnfilled = 0;
    let openUnfilled = 0;

    let sec1Unfilled = 0;
    for (let q = 1; q <= 32; q++) {
      const item = this.answers[String(q)];
      if (!item || !item.ans || !String(item.ans).trim()) {
        closedUnfilled++;
        sec1Unfilled++;
      }
    }

    let sec2Unfilled = 0;
    for (let q = 33; q <= 35; q++) {
      const item = this.answers[String(q)];
      if (!item || !item.ans || !String(item.ans).trim()) {
        closedUnfilled++;
        sec2Unfilled++;
      }
    }

    for (let q = 36; q <= 45; q++) {
      for (let sub of ['a', 'b']) {
        const item = this.answers[`${q}${sub}`];
        if (!item || !item.ans || !String(item.ans).trim()) {
          openUnfilled++;
        }
      }
    }

    const totalUnfilled = closedUnfilled + openUnfilled;
    const totalQuestions = 55;
    const totalFilled = totalQuestions - totalUnfilled;

    // 1. Top status bar
    const totalBadge = document.getElementById('unfilled-total-badge');
    const statusIcon = document.getElementById('unfilled-status-icon');
    const statusTitle = document.getElementById('unfilled-status-title');
    const closedCountEl = document.getElementById('unfilled-closed-count');
    const openCountEl = document.getElementById('unfilled-open-count');

    if (totalBadge) {
      if (totalUnfilled === 0) {
        totalBadge.textContent = '✅ Barchasi to\'ldirildi (55/55)';
        totalBadge.style.background = '#10B981';
        if (statusIcon) statusIcon.textContent = '🎉';
        if (statusTitle) statusTitle.textContent = 'Barcha savollar tayyor:';
      } else {
        totalBadge.textContent = `${totalUnfilled} ta belgilanmagan (${totalFilled}/55)`;
        totalBadge.style.background = '#EF4444';
        if (statusIcon) statusIcon.textContent = '⚠️';
        if (statusTitle) statusTitle.textContent = 'Javoblar to\'ldirilishi:';
      }
    }

    if (closedCountEl) {
      if (closedUnfilled === 0) {
        closedCountEl.textContent = '✅ Barchasi belgilandi (35/35)';
        closedCountEl.style.color = '#10B981';
      } else {
        closedCountEl.textContent = `${closedUnfilled} ta belgilanmagan (${35 - closedUnfilled}/35)`;
        closedCountEl.style.color = '#EF4444';
      }
    }

    if (openCountEl) {
      if (openUnfilled === 0) {
        openCountEl.textContent = '✅ Barchasi kiritildi (20/20)';
        openCountEl.style.color = '#10B981';
      } else {
        openCountEl.textContent = `${openUnfilled} ta kiritilmagan (${20 - openUnfilled}/20)`;
        openCountEl.style.color = '#EF4444';
      }
    }

    // 2. Section Subtexts
    const sec1El = document.getElementById('cnt-sec-1');
    if (sec1El) {
      if (sec1Unfilled === 0) {
        sec1El.textContent = '✅ Barchasi belgilandi (32/32)';
        sec1El.style.color = '#10B981';
      } else {
        sec1El.textContent = `⚠️ ${sec1Unfilled} ta belgilanmagan`;
        sec1El.style.color = '#EF4444';
      }
    }

    const sec2El = document.getElementById('cnt-sec-2');
    if (sec2El) {
      if (sec2Unfilled === 0) {
        sec2El.textContent = '✅ Barchasi belgilandi (3/3)';
        sec2El.style.color = '#10B981';
      } else {
        sec2El.textContent = `⚠️ ${sec2Unfilled} ta belgilanmagan`;
        sec2El.style.color = '#EF4444';
      }
    }

    const sec3El = document.getElementById('cnt-sec-3');
    if (sec3El) {
      if (openUnfilled === 0) {
        sec3El.textContent = '✅ Barchasi kiritildi (20/20)';
        sec3El.style.color = '#10B981';
      } else {
        sec3El.textContent = `⚠️ ${openUnfilled} ta kiritilmagan`;
        sec3El.style.color = '#EF4444';
      }
    }

    // 3. Bottom Dock
    const dockUnfilled = document.getElementById('admin-dock-unfilled');
    if (dockUnfilled) {
      if (totalUnfilled === 0) {
        dockUnfilled.textContent = '✅ 55/55 to\'liq belgilandi';
        dockUnfilled.style.color = '#10B981';
      } else {
        dockUnfilled.textContent = `⚠️ ${totalUnfilled} ta javob qoldi (Yopiq: ${closedUnfilled}, Ochiq: ${openUnfilled})`;
        dockUnfilled.style.color = '#EF4444';
      }
    }

    return { totalUnfilled, closedUnfilled, openUnfilled };
  },

  async saveTest() {
    const title = (document.getElementById('adm-test-title')?.value || '').trim() || 'Matematika Milliy Sertifikat Testi';
    const subject = (document.getElementById('adm-test-subject')?.value || '').trim() || 'Matematika';
    let code = (document.getElementById('adm-test-code')?.value || '').trim().toUpperCase();
    const timeLimit = parseInt(document.getElementById('adm-test-time')?.value) || 0;

    if (!code) {
      code = 'TEST-' + Math.floor(1000 + Math.random() * 9000);
    }

    // 36a-45b savollarni to'g'ridan-to'g'ri DOM inputlaridan ham tekshirib olish (100% kafolat)
    for (let q = 36; q <= 45; q++) {
      for (let sub of ['a', 'b']) {
        const key = `${q}${sub}`;
        const input = document.getElementById(`input-${key}`);
        if (!this.answers[key]) {
          this.answers[key] = { ans: '', score: 1.5 };
        }
        if (input && input.value !== undefined) {
          this.answers[key].ans = input.value.trim();
        }
      }
    }

    const { totalUnfilled, closedUnfilled, openUnfilled } = this.updateUnfilledStats();

    if (totalUnfilled > 0) {
      const confirmMsg = `⚠️ DIQQAT! Jami 55 ta savoldan ${totalUnfilled} tasiga javob belgilanmagan:\n\n` +
        `• 🔘 Yopiq savollarda (1-35): ${closedUnfilled} ta belgilanmagan\n` +
        `• ✍️ Ochiq savollarda (36-45): ${openUnfilled} ta kiritilmagan\n\n` +
        `Iltimos, avval barcha savollarga to'g'ri javobni belgilang!`;
      
      if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.showAlert) {
        window.Telegram.WebApp.showAlert(confirmMsg);
      } else {
        alert(confirmMsg);
      }
      return;
    }

    const keyCodeInput = document.getElementById('adm-test-key-code');
    const keyCode = keyCodeInput ? keyCodeInput.value.trim() : '';

    const payload = {
      test_code: code,
      title: title,
      subject: subject,
      time_limit_min: timeLimit,
      key_access_code: keyCode,
      answers: this.answers
    };

    const saveBtn = document.querySelector('.btn-submit-test');
    if (saveBtn) {
      saveBtn.disabled = true;
      saveBtn.textContent = 'Saqlanmoqda... ⏳';
    }

    try {
      const response = await fetch('/api/create-test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const res = await response.json();
      if (res.success) {
        if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.showAlert) {
          window.Telegram.WebApp.showAlert('✅ Test muvaffaqiyatli saqlandi va e\'lon qilindi!');
          setTimeout(() => {
            window.Telegram.WebApp.close();
          }, 800);
        } else {
          alert('✅ Test muvaffaqiyatli saqlandi va e\'lon qilindi!');
          window.location.reload();
        }
      } else {
        if (saveBtn) {
          saveBtn.disabled = false;
          saveBtn.textContent = '💾 Testni saqlash';
        }
        alert(res.message || 'Saqlashda xatolik yuz berdi!');
      }
    } catch (e) {
      if (saveBtn) {
        saveBtn.disabled = false;
        saveBtn.textContent = '💾 Testni saqlash';
      }
      alert('Server bilan bog\'lanishda xatolik: ' + e.message);
    }
  }
};

window.AdminApp = AdminApp;

document.addEventListener('DOMContentLoaded', () => {
  AdminApp.init();
});
