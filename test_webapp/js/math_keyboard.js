/**
 * Interaktiv Matematik Klaviatura (Virtual Math Keyboard)
 * Har qanday son, amal, belgi, ildiz, formula va erkin matnlarni kiritish imkoniyati
 */
const MathKeyboard = {
  activeFieldKey: null,
  activeInputElement: null,
  activeFieldOrder: [],

  init() {
    // 36a dan 45b gacha bo'lgan maydonlar ketma-ketligini tuzish
    this.activeFieldOrder = [];
    for (let q = 36; q <= 45; q++) {
      this.activeFieldOrder.push(`${q}a`);
      this.activeFieldOrder.push(`${q}b`);
    }
  },

  openFor(fieldKey) {
    this.activeFieldKey = fieldKey;
    const inputEl = document.getElementById(`input-${fieldKey}`) || document.getElementById(`adm-input-${fieldKey}`);
    this.activeInputElement = inputEl;

    const panel = document.getElementById('math-keyboard-panel');
    const targetName = document.getElementById('keyboard-target-name');
    const liveInput = document.getElementById('keyboard-live-input');

    if (targetName) targetName.textContent = fieldKey.toUpperCase();
    if (liveInput && inputEl) {
      liveInput.value = inputEl.value || '';
    }

    if (panel) {
      panel.classList.add('open');
    }

    // Input qutisini aktiv deb belgilash
    document.querySelectorAll('.savol-input-box').forEach(b => b.classList.remove('focused'));
    const boxEl = document.getElementById(`box-${fieldKey}`);
    if (boxEl) {
      boxEl.classList.add('focused');
      boxEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.HapticFeedback) {
      window.Telegram.WebApp.HapticFeedback.impactOccurred('light');
    }
  },

  close() {
    const panel = document.getElementById('math-keyboard-panel');
    if (panel) panel.classList.remove('open');
    document.querySelectorAll('.savol-input-box').forEach(b => b.classList.remove('focused'));
    this.activeFieldKey = null;
    this.activeInputElement = null;
  },

  onLiveInput(val) {
    if (!this.activeFieldKey) return;
    if (this.activeInputElement) {
      this.activeInputElement.value = val;
    }
    
    if (typeof TestApp !== 'undefined' && TestApp.setOpenAnswer) {
      TestApp.setOpenAnswer(this.activeFieldKey, val);
    } else if (window.TestApp && window.TestApp.setOpenAnswer) {
      window.TestApp.setOpenAnswer(this.activeFieldKey, val);
    }

    if (typeof AdminApp !== 'undefined' && AdminApp.updateOpenAns) {
      AdminApp.updateOpenAns(this.activeFieldKey, val);
    } else if (window.AdminApp && window.AdminApp.updateOpenAns) {
      window.AdminApp.updateOpenAns(this.activeFieldKey, val);
    }

    const boxEl = document.getElementById(`box-${this.activeFieldKey}`);
    if (boxEl) {
      boxEl.classList.toggle('filled', (val || '').trim().length > 0);
    }
  },

  insert(val) {
    if (!this.activeFieldKey) return;
    
    const liveInput = document.getElementById('keyboard-live-input');
    const targetInput = this.activeInputElement || liveInput;
    if (!targetInput) return;

    const start = targetInput.selectionStart ?? targetInput.value.length;
    const end = targetInput.selectionEnd ?? targetInput.value.length;
    const text = targetInput.value || '';

    const newVal = text.substring(0, start) + val + text.substring(end);
    targetInput.value = newVal;
    if (liveInput && liveInput !== targetInput) liveInput.value = newVal;
    if (this.activeInputElement && this.activeInputElement !== targetInput) this.activeInputElement.value = newVal;

    const newPos = start + val.length;
    if (targetInput.setSelectionRange) {
      try { targetInput.setSelectionRange(newPos, newPos); } catch (e) {}
    }

    this.onInputChange();
  },

  backspace() {
    if (!this.activeFieldKey) return;
    const liveInput = document.getElementById('keyboard-live-input');
    const targetInput = this.activeInputElement || liveInput;
    if (!targetInput) return;

    const start = targetInput.selectionStart ?? targetInput.value.length;
    const end = targetInput.selectionEnd ?? targetInput.value.length;
    const text = targetInput.value || '';

    let newVal = text;
    let newPos = start;

    if (start === end && start > 0) {
      newVal = text.substring(0, start - 1) + text.substring(end);
      newPos = start - 1;
    } else if (start !== end) {
      newVal = text.substring(0, start) + text.substring(end);
      newPos = start;
    }

    targetInput.value = newVal;
    if (liveInput && liveInput !== targetInput) liveInput.value = newVal;
    if (this.activeInputElement && this.activeInputElement !== targetInput) this.activeInputElement.value = newVal;

    if (targetInput.setSelectionRange) {
      try { targetInput.setSelectionRange(newPos, newPos); } catch (e) {}
    }

    this.onInputChange();
  },

  clear() {
    if (!this.activeFieldKey) return;
    if (this.activeInputElement) this.activeInputElement.value = '';
    const liveInput = document.getElementById('keyboard-live-input');
    if (liveInput) liveInput.value = '';
    this.onInputChange();
  },

  onInputChange() {
    if (!this.activeFieldKey) return;
    const liveInput = document.getElementById('keyboard-live-input');
    const val = (this.activeInputElement ? this.activeInputElement.value : '') || (liveInput ? liveInput.value : '');
    
    // Asosiy TestApp holatiga saqlash
    if (typeof TestApp !== 'undefined' && TestApp.setOpenAnswer) {
      TestApp.setOpenAnswer(this.activeFieldKey, val);
    } else if (window.TestApp && window.TestApp.setOpenAnswer) {
      window.TestApp.setOpenAnswer(this.activeFieldKey, val);
    }

    if (typeof AdminApp !== 'undefined' && AdminApp.updateOpenAns) {
      AdminApp.updateOpenAns(this.activeFieldKey, val);
    } else if (window.AdminApp && window.AdminApp.updateOpenAns) {
      window.AdminApp.updateOpenAns(this.activeFieldKey, val);
    }

    // Box indicator
    const boxEl = document.getElementById(`box-${this.activeFieldKey}`);
    if (boxEl) {
      boxEl.classList.toggle('filled', (val || '').trim().length > 0);
    }

    if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.HapticFeedback) {
      window.Telegram.WebApp.HapticFeedback.selectionChanged();
    }
  },

  prevField() {
    if (!this.activeFieldKey) return;
    const idx = this.activeFieldOrder.indexOf(this.activeFieldKey);
    if (idx > 0) {
      this.openFor(this.activeFieldOrder[idx - 1]);
    }
  },

  nextField() {
    if (!this.activeFieldKey) return;
    const idx = this.activeFieldOrder.indexOf(this.activeFieldKey);
    if (idx < this.activeFieldOrder.length - 1) {
      this.openFor(this.activeFieldOrder[idx + 1]);
    }
  },

  switchTab(tab) {
    const btnMath = document.getElementById('kb-tab-math');
    const btnFunc = document.getElementById('kb-tab-func');
    const btnVars = document.getElementById('kb-tab-vars');

    const bodyMath = document.getElementById('keyboard-body-math');
    const bodyFunc = document.getElementById('keyboard-body-func');
    const bodyVars = document.getElementById('keyboard-body-vars');

    if (btnMath) btnMath.classList.toggle('active', tab === 'math');
    if (btnFunc) btnFunc.classList.toggle('active', tab === 'func');
    if (btnVars) btnVars.classList.toggle('active', tab === 'vars');

    if (bodyMath) bodyMath.style.display = tab === 'math' ? 'flex' : 'none';
    if (bodyFunc) bodyFunc.style.display = tab === 'func' ? 'flex' : 'none';
    if (bodyVars) bodyVars.style.display = tab === 'vars' ? 'flex' : 'none';
  }
};

window.MathKeyboard = MathKeyboard;

document.addEventListener('DOMContentLoaded', () => {
  MathKeyboard.init();
});
