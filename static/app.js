document.addEventListener('DOMContentLoaded', () => {
  const role = document.getElementById('role');
  const studentFields = document.getElementById('student-fields');
  const parentFields = document.getElementById('parent-fields');
  function updateRole() {
    if (!role) return;
    const student = role.value === 'student';
    const parent = role.value === 'parent';
    studentFields?.classList.toggle('hidden', !student);
    parentFields?.classList.toggle('hidden', !parent);
    if (studentFields) studentFields.querySelectorAll('input,select').forEach(el => { el.required = student && ['region','district','state','board','grade'].includes(el.name); });
  }
  role?.addEventListener('change', updateRole); updateRole();
  document.querySelectorAll('[data-prompt]').forEach(btn => btn.addEventListener('click', () => {
    const prompt = document.getElementById('prompt'); if (prompt) { prompt.value = btn.dataset.prompt; prompt.focus(); }
  }));
  const subject = document.getElementById('assistant-subject');
  const topic = document.getElementById('assistant-topic');
  function updateTopics() {
    if (!subject || !topic || !window.VIDHYASTRA_TOPICS) return;
    topic.innerHTML = '';
    (window.VIDHYASTRA_TOPICS[subject.value] || []).forEach(t => { const opt=document.createElement('option'); opt.value=t; opt.textContent=t; topic.appendChild(opt); });
  }
  subject?.addEventListener('change', updateTopics); updateTopics();
});
