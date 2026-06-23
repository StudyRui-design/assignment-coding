// ============================================================
// Recruitment Role Data Analytics - Frontend Script
// ECharts Charts - AI Prediction - AI Chat
// ============================================================

var charts = {};
var ECHARTS_READY = (typeof echarts !== 'undefined');
var modelsData = {};
var CHAT_SESSION = 'recruitment_' + Date.now();
var isChatting = false;

window.addEventListener('error', function(e) {
  // 静默处理 CDN 资源加载失败
  var target = e.target || e.srcElement;
  if (target && (target.tagName === 'SCRIPT' || target.tagName === 'LINK')) {
    console.warn('Resource load failed:', target.src || target.href);
    e.preventDefault();
    return;
  }
  // 静默处理已知的良性错误
  var msg = e.message || '';
  if (msg.indexOf('getBoundingClientRect') !== -1 || msg.indexOf('Script error') !== -1) {
    console.warn('Suppressed error:', msg);
    e.preventDefault();
    return;
  }
}, true);

// ===== Tab switching =====
function switchPage(name) {
    document.querySelectorAll('.page').forEach(function(p) { p.classList.remove('active'); });
    document.getElementById('page-' + name).classList.add('active');
    document.querySelectorAll('.nav-tabs button').forEach(function(b) { b.classList.remove('active'); b.removeAttribute('aria-current'); });
    var btns = document.querySelectorAll('.nav-tabs button');
    if (name === 'dashboard' && btns[0]) { btns[0].classList.add('active'); btns[0].setAttribute('aria-current', 'page'); }
    else if (name === 'predict' && btns[1]) { btns[1].classList.add('active'); btns[1].setAttribute('aria-current', 'page'); }
    else if (name === 'chat' && btns[2]) { btns[2].classList.add('active'); btns[2].setAttribute('aria-current', 'page'); }
    // Resize charts on switch
    setTimeout(function() { Object.keys(charts).forEach(function(k) { try { if (charts[k]) charts[k].resize(); } catch(e) {} }); }, 200);
}

// ===== Particle background =====
(function() {
    var canvas = document.getElementById('particles');
    if (!canvas) return;
    var ctx = canvas.getContext('2d');
    var particles = [];
    function resizeCanvas() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
    resizeCanvas(); window.addEventListener('resize', resizeCanvas);
    var Particle = function() { this.reset(); };
    Particle.prototype.reset = function() { this.x = Math.random()*canvas.width; this.y = Math.random()*canvas.height; this.size = Math.random()*1.5+0.5; this.speedX = (Math.random()-0.5)*0.3; this.speedY = (Math.random()-0.5)*0.3; this.opacity = Math.random()*0.5+0.1; };
    Particle.prototype.update = function() { this.x += this.speedX; this.y += this.speedY; if (this.x<0||this.x>canvas.width) this.speedX *= -1; if (this.y<0||this.y>canvas.height) this.speedY *= -1; };
    Particle.prototype.draw = function() { ctx.beginPath(); ctx.arc(this.x,this.y,this.size,0,Math.PI*2); ctx.fillStyle = 'rgba(0,212,255,'+this.opacity+')'; ctx.fill(); };
    var PARTICLE_COUNT = window.innerWidth<768?40:80;
    var CONNECT_DIST = window.innerWidth<768?70:120;
    for (var i=0;i<PARTICLE_COUNT;i++) particles.push(new Particle());
    var _animRunning = true;
    function animateParticles() {
        if (!_animRunning) { requestAnimationFrame(animateParticles); return; }
        ctx.clearRect(0,0,canvas.width,canvas.height);
        for (var i=0;i<particles.length;i++) { particles[i].update(); particles[i].draw(); }
        for (var i=0;i<particles.length;i++) for (var j=i+1;j<particles.length;j++) { var dx=particles[i].x-particles[j].x; var dy=particles[i].y-particles[j].y; var dist=Math.sqrt(dx*dx+dy*dy); if (dist<CONNECT_DIST) { ctx.beginPath(); ctx.moveTo(particles[i].x,particles[i].y); ctx.lineTo(particles[j].x,particles[j].y); ctx.strokeStyle='rgba(0,212,255,'+(0.06*(1-dist/CONNECT_DIST))+')'; ctx.lineWidth=0.5; ctx.stroke(); } }
        requestAnimationFrame(animateParticles);
    }
    animateParticles();
    document.addEventListener('visibilitychange', function() { _animRunning = !document.hidden; });
})();

function initChart(id) {
  if (!ECHARTS_READY) return null;
  var dom = document.getElementById(id);
  if (!dom) return null;
  try {
    if (charts[id]) { charts[id].dispose(); delete charts[id]; }
    var chart = echarts.init(dom);
    if (!chart) return null;
    charts[id] = chart;
    var skeleton = dom.querySelector('.chart-skeleton');
    if (skeleton) skeleton.style.display = 'none';
    return chart;
  } catch(e) { console.warn('Chart init failed:', id, e.message); return null; }
}

function _chartFallback(id, msg) {
  var dom = document.getElementById(id);
  if (!dom) return;
  var skeleton = dom.querySelector('.chart-skeleton');
  if (skeleton) skeleton.innerHTML = '<div class="chart-fallback"><span>'+msg+'</span></div>';
}

window.addEventListener('resize', function() {
  Object.keys(charts).forEach(function(k) { try { if (charts[k]) charts[k].resize(); } catch(e) {} });
});

function loadStats() {
  fetch('/api/stats').then(function(r){return r.json();}).then(function(d){
    var setStat = function(key, html) { var el = document.querySelector('.stat-card[data-stat="'+key+'"] .value'); if (el) el.innerHTML = html; };
    setStat('total', d.total_jobs);
    setStat('avg', d.avg_salary + ' <small style="font-size:14px;color:#8892b0">K/月</small>');
    setStat('max', d.max_salary + ' <small style="font-size:14px;color:#8892b0">K/月</small>');
    setStat('city', d.top_city);
    var sub = document.getElementById('city-sub');
    if (sub) sub.textContent = '共 ' + d.city_count + ' 城市';
  }).catch(function(e){ console.warn('Stats error:', e.message); });
}

function renderPieChart(id, data, name) {
  var chart = initChart(id); if (!chart) return;
  chart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    series: [{ type: 'pie', radius: ['30%', '65%'], center: ['50%', '50%'],
      label: { color: '#e6f1ff', fontSize: 11 },
      labelLine: { lineStyle: { color: 'rgba(0,212,255,0.2)' } },
      data: data.map(function(v){ return {value: v.value, name: v.name||''}; })
    }]
  });
}

function renderBarChart(id, data, opts) {
  var chart = initChart(id); if (!chart) return;
  var isHoriz = opts && opts.horizontal;
  var cfg = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '8%', bottom: '8%', containLabel: true },
    xAxis: isHoriz ? { type: 'value', axisLabel: { color: '#8892b0' }, splitLine: { lineStyle: { color: 'rgba(0,212,255,0.06)' } } } : { type: 'category', data: data.labels, axisLabel: { color: '#8892b0', rotate: data.labels.length > 8 ? 30 : 0 }, axisLine: { lineStyle: { color: 'rgba(0,212,255,0.15)' } } },
    yAxis: isHoriz ? { type: 'category', data: data.labels, axisLabel: { color: '#e6f1ff' }, axisLine: { show: false }, axisTick: { show: false } } : { type: 'value', axisLabel: { color: '#8892b0' }, splitLine: { lineStyle: { color: 'rgba(0,212,255,0.06)' } } },
    series: [{ type: 'bar', data: data.values.map(function(v,i){ return {value:v, itemStyle:{color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:opts&&opts.color?opts.color:'#00d4ff'},{offset:1,color:opts&&opts.color2?opts.color2:'#4d9eff'}])}}; }), barWidth: '50%', label: { show: data.values.length <= 15, position: 'top', color: '#8892b0', fontSize: 11 } }]
  };
  if (isHoriz) { cfg.xAxis.type = 'value'; cfg.yAxis.type = 'category'; cfg.series[0].label.position = 'right'; }
  chart.setOption(cfg);
}

function loadAllCharts() {
  loadStats();

  // City distribution
  fetch('/api/city_distribution').then(function(r){return r.json();}).then(function(d){ renderBarChart('chart-city', d, {color:'#00d4ff',color2:'#2979ff'}); }).catch(function(e){ _chartFallback('chart-city','Failed'); });

  // Education
  fetch('/api/education_distribution').then(function(r){return r.json();}).then(function(d){ renderPieChart('chart-education', d.labels.map(function(n,i){return{name:n,value:d.values[i]};})); }).catch(function(e){ _chartFallback('chart-education','Failed'); });

  // Com type
  fetch('/api/com_type_distribution').then(function(r){return r.json();}).then(function(d){ renderPieChart('chart-comtype', d.labels.map(function(n,i){return{name:n,value:d.values[i]};})); }).catch(function(e){ _chartFallback('chart-comtype','Failed'); });

  // Company TOP15
  fetch('/api/company_top15').then(function(r){return r.json();}).then(function(d){ renderBarChart('chart-company', d, {color:'#00e676',color2:'#00c853'}); }).catch(function(e){ _chartFallback('chart-company','Failed'); });

  // Work year salary
  fetch('/api/workyear_salary').then(function(r){return r.json();}).then(function(d){
    if (d.data && d.data.length) { renderBarChart('chart-workyear', {labels:d.data.map(function(i){return i.work_year;}), values:d.data.map(function(i){return i.avg_salary;})}, {color:'#ff9100',color2:'#ff6d00'}); }
    else _chartFallback('chart-workyear','No data');
  }).catch(function(e){ _chartFallback('chart-workyear','Failed'); });

  // Salary distribution
  fetch('/api/salary_distribution').then(function(r){return r.json();}).then(function(d){ renderBarChart('chart-salary', d, {color:'#b388ff',color2:'#7c4dff'}); }).catch(function(e){ _chartFallback('chart-salary','Failed'); });

  // Company size
  fetch('/api/com_size_distribution').then(function(r){return r.json();}).then(function(d){ renderPieChart('chart-comsize', d.labels.map(function(n,i){return{name:n,value:d.values[i]};})); }).catch(function(e){ _chartFallback('chart-comsize','Failed'); });

  // Wordcloud
  fetch('/api/benefits_words').then(function(r){return r.json();}).then(function(d){
    if (typeof echarts === 'undefined') return;
    var dom = document.getElementById('chart-wordcloud'); if (!dom) return;
    if (charts['chart-wordcloud']) { charts['chart-wordcloud'].dispose(); delete charts['chart-wordcloud']; }
    var skeleton = dom.querySelector('.chart-skeleton');
    if (skeleton) skeleton.style.display = 'none';

    // 尝试 wordCloud，扩展未加载则自动降级为横向柱状图
    try {
      var chart = echarts.init(dom); charts['chart-wordcloud'] = chart;
      chart.setOption({
        tooltip: { show: true, formatter: function(p){return p.data.name+': '+p.data.value+' 次';} },
        series: [{ type: 'wordCloud', gridSize: 14, sizeRange: [14, 60], rotationRange: [-30, 30], shape: 'circle', textStyle: { color: function(){return 'rgb('+[Math.round(Math.random()*160+50),Math.round(Math.random()*160+50),Math.round(Math.random()*200+55)].join(',')+')';} }, data: d.map(function(x){return{name:x.name,value:x.value};}) }]
      });
    } catch(e) {
      // wordCloud 不可用 → 降级为横向柱状图
      if (charts['chart-wordcloud']) { charts['chart-wordcloud'].dispose(); delete charts['chart-wordcloud']; }
      var fallbackChart = echarts.init(dom); charts['chart-wordcloud'] = fallbackChart;
      var top30 = d.slice(0, 30).sort(function(a,b){return a.value - b.value;});
      fallbackChart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '3%', right: '8%', bottom: '3%', containLabel: true },
        xAxis: { type: 'value', axisLabel: { color: '#8892b0' }, splitLine: { lineStyle: { color: 'rgba(0,212,255,0.06)' } } },
        yAxis: { type: 'category', data: top30.map(function(x){return x.name;}), axisLabel: { color: '#e6f1ff', fontSize: 11 }, axisLine: { show: false }, axisTick: { show: false }, splitLine: { show: false } },
        series: [{ type: 'bar', data: top30.map(function(x){return {value:x.value,itemStyle:{color:new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#00d4ff'},{offset:1,color:'#7c4dff'}])}};}), barWidth: '55%', label: { show: true, position: 'right', color: '#8892b0', fontSize: 11 }, animationDuration: 800 }]
      });
    }
  }).catch(function(e){ _chartFallback('chart-wordcloud','Failed'); });

  // Model info
  fetch('/api/models_info').then(function(r){return r.json();}).then(function(d){
    modelsData = d;
    var cards = document.querySelectorAll('#models-grid .model-score-card');
    var keys = ['decision_tree', 'linear_regression', 'random_forest', 'random_forest_salary'];
    var colors = ['#00d4ff', '#00e676', '#ff9100', '#b388ff'];
    keys.forEach(function(k, i) {
      if (d[k] && cards[i]) {
        var scoreEl = cards[i].querySelector('.m-score');
        scoreEl.textContent = d[k].metric_value;
        scoreEl.style.color = colors[i];
        if (d[k].feature_importance && d[k].feature_importance.length > 0) {
          var sorted = d[k].feature_importance.sort(function(a,b){return b.importance-a.importance;});
          var topFeat = sorted[0];
          var metricEl = cards[i].querySelector('.m-metric');
          metricEl.innerHTML = d[k].metric_name + '<br><span style="font-size:10px;color:var(--text-muted)">Top: ' + topFeat.feature + '</span>';
        }
      }
    });
  }).catch(function(e){ console.warn('Models info error:', e.message); });

  // Form options + auto predict
  fetch('/api/form_options').then(function(r){return r.json();}).then(function(data){
    var fields = { 'input-city': data.city, 'input-education': data.education, 'input-workyear': data.work_year, 'input-comtype': data.com_type, 'input-comsize': data.com_size };
    Object.entries(fields).forEach(function(e){ var id=e[0], opts=e[1]; var sel=document.getElementById(id); if(sel){ sel.innerHTML=opts.map(function(o){return '<option value="'+o+'">'+o+'</option>';}).join(''); if(id==='input-city'&&opts.includes('北京')) sel.value='北京'; if(id==='input-education'&&opts.includes('本科')) sel.value='本科'; if(id==='input-workyear'&&opts.includes('3-5年')) sel.value='3-5年'; } });
    }).catch(function(e){ console.warn('Form options error:', e.message); })
    .then(function(){ setTimeout(doPredict, 300); });
}

function doPredict() {
  var btn = document.getElementById('btn-predict');
  if (!btn) return;
  btn.disabled = true;
  btn.textContent = '分析中...';

  var getVal = function(id) { var el = document.getElementById(id); return el ? el.value : ''; };
  var payload = { city: getVal('input-city')||'北京', education: getVal('input-education')||'本科', work_year: getVal('input-workyear')||'3-5年', com_type: getVal('input-comtype')||'互联网', com_size: getVal('input-comsize')||'100-499人' };

  fetch('/api/predict', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
  .then(function(r){return r.json();}).then(function(data){
    var html = '';
    // Decision Tree
    if (data.decision_tree && !data.decision_tree.error) {
      var dt = data.decision_tree; var top3 = dt.top3 || [];
      html += '<div class="result-card"><h4>🌲 决策树 · 热门城市预测</h4>' +
        '<div class="result-row"><span class="r-label">预测城市</span><span class="r-value" style="color:#00d4ff">' + dt.predicted_city + '</span></div>' +
        '<div style="margin-top:10px;font-size:12px;color:var(--text-secondary)">城市概率分布：</div>' +
        top3.map(function(t){return '<div class="result-row" style="font-size:13px"><span style="color:var(--text-secondary)">'+t.city+'</span><span style="color:var(--accent-cyan);font-weight:600">'+t.prob.toFixed(1)+'%</span></div>';}).join('') +
        '</div>';
    }
    // Linear Regression
    if (data.linear_regression && !data.linear_regression.error) {
      var lr = data.linear_regression;
      html += '<div class="result-card"><h4>📈 线性回归 · 薪资预测</h4>' +
        '<div class="result-row"><span class="r-label">预测薪资</span><span class="r-value" style="color:#00e676">' + lr.predicted_salary_k + ' K</span></div>' +
        '<div class="result-row" style="font-size:13px"><span class="r-label">预估范围</span><span style="color:var(--accent-cyan)">' + lr.predicted_salary_range + '</span></div>' +
        '</div>';
    }
    // RF Intensity
    if (data.random_forest && !data.random_forest.error) {
      var rf = data.random_forest; var lvlColors = { '高': '#00e676', '中': '#ffd740', '低': '#ff5252' };
      html += '<div class="result-card"><h4>🌳 随机森林 · 招聘强度预测</h4>' +
        '<div class="result-row"><span class="r-label">招聘强度评分</span><span class="r-value" style="color:#ff9100">' + rf.intensity_score + ' / 100</span></div>' +
        '<div class="intensity-bar"><div class="fill" style="width:' + rf.intensity_score + '%"></div></div>' +
        '<div class="intensity-level" style="color:' + (lvlColors[rf.intensity_level] || '#8892b0') + ';font-weight:600">强度等级：' + rf.intensity_level + '</div>' +
        '<div class="result-row" style="font-size:13px;margin-top:6px"><span class="r-label">原始预测值</span><span style="color:var(--text-secondary)">' + rf.predicted_intensity + ' 岗位/组合</span></div>' +
        '</div>';
    }
    // RF Salary
    if (data.random_forest_salary && !data.random_forest_salary.error) {
      var rfs = data.random_forest_salary;
      html += '<div class="result-card"><h4>📈 随机森林 · 薪资预测</h4>' +
        '<div class="result-row"><span class="r-label">预测薪资</span><span class="r-value" style="color:#b388ff">' + rfs.predicted_salary_k + ' K</span></div>' +
        '<div class="result-row" style="font-size:13px"><span class="r-label">预估范围</span><span style="color:var(--accent-cyan)">' + rfs.predicted_salary_range + '</span></div>' +
        '</div>';
    }
    // Errors
    Object.entries(data).forEach(function(e){ var k=e[0],v=e[1]; if(v&&v.error){ html+='<div class="result-card" style="border-color:#ff5252"><h4 style="color:#ff5252">⚠ Error ('+k+')</h4><p style="color:var(--text-secondary);font-size:13px">'+v.error+'</p></div>'; } });

    document.getElementById('predict-results').innerHTML = html;
    doSalaryCompare();
    btn.disabled = false; btn.textContent = '⚡ 开始预测';
  }).catch(function(err){
    document.getElementById('predict-results').innerHTML = '<div class="result-card" style="border-color:#ff5252;text-align:center"><h4 style="color:#ff5252">⚠ Error</h4><p style="color:var(--text-secondary);font-size:13px">'+err.message+'</p></div>';
    btn.disabled = false; btn.textContent = '⚡ 开始预测';
  });
}

function doSalaryCompare() {
  var getVal = function(id) { var el = document.getElementById(id); return el ? el.value : ''; };
  var payload = { city: getVal('input-city')||'北京', education: getVal('input-education')||'本科', work_year: getVal('input-workyear')||'3-5年', com_type: getVal('input-comtype')||'互联网', com_size: getVal('input-comsize')||'100-499人' };

  fetch('/api/salary/compare', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
  .then(function(r){return r.json();}).then(function(data){
    if (data.linear_regression && !data.linear_regression.error) {
      var lr = data.linear_regression;
      document.getElementById('cmp-lr-salary').textContent = lr.predicted_salary_k + ' K';
      document.getElementById('cmp-lr-r2').textContent = lr.metrics ? lr.metrics.r2 : '--';
      document.getElementById('cmp-lr-rmse').textContent = lr.metrics ? lr.metrics.rmse : '--';
      document.getElementById('cmp-lr-mae').textContent = lr.metrics ? lr.metrics.mae : '--';
    }
    if (data.random_forest && !data.random_forest.error) {
      var rf = data.random_forest;
      document.getElementById('cmp-rf-salary').textContent = rf.predicted_salary_k + ' K';
      document.getElementById('cmp-rf-r2').textContent = rf.metrics ? rf.metrics.r2 : '--';
      document.getElementById('cmp-rf-rmse').textContent = rf.metrics ? rf.metrics.rmse : '--';
      document.getElementById('cmp-rf-mae').textContent = rf.metrics ? rf.metrics.mae : '--';
    }
    renderModelCompareChart(data.linear_regression, data.random_forest);
    if (data.random_forest && data.random_forest.feature_importance) {
      renderFeatureImportance(data.random_forest.feature_importance);
    }
  }).catch(function(e){ console.warn('Salary compare error:', e.message); });
}

function renderModelCompareChart(lrData, rfData) {
  if (typeof echarts === 'undefined') return;
  var dom = document.getElementById('chart-model-compare');
  if (!dom) return;
  if (charts['model-compare']) { charts['model-compare'].dispose(); delete charts['model-compare']; }
  try {
    var chart = echarts.init(dom); charts['model-compare'] = chart;
    var skeleton = dom.querySelector('.chart-skeleton'); if (skeleton) skeleton.style.display = 'none';
    var metrics = ['R²', 'RMSE', 'MAE'];
    var lrM = lrData && lrData.metrics ? lrData.metrics : {};
    var rfM = rfData && rfData.metrics ? rfData.metrics : {};
    var lrVals = lrData ? [ Math.max(0, (lrM.r2||0)*100), Math.min(100, (lrM.rmse||10)*10), Math.min(100, (lrM.mae||8)*12.5) ] : [0,0,0];
    var rfVals = rfData ? [ Math.max(0, (rfM.r2||0)*100), Math.min(100, (rfM.rmse||10)*10), Math.min(100, (rfM.mae||8)*12.5) ] : [0,0,0];
    chart.setOption({
      tooltip: { trigger: 'item', backgroundColor: 'rgba(15,31,58,0.95)', borderColor: 'rgba(0,212,255,0.2)', textStyle: { color: '#e6f1ff' }, formatter: function(p){ var vals=p.value; var html='<div style="font-weight:600;margin-bottom:6px;">'+p.name+'</div>'; metrics.forEach(function(m,i){ html+='<div style="display:flex;justify-content:space-between;gap:16px;font-size:13px;margin:3px 0;"><span style="color:#8892b0;">'+m+'</span><span style="color:var(--accent-cyan);font-weight:600;">'+vals[i].toFixed(1)+'</span></div>'; }); return html; } },
      legend: { data: ['线性回归', '随机森林'], textStyle: { color: '#8892b0', fontSize: 13 }, top: 8 },
      radar: { indicator: metrics.map(function(m){return{name:m,max:100};}), shape: 'polygon', center: ['50%', '55%'], radius: '68%', axisName: { color: '#e6f1ff', fontSize: 13, fontWeight: 500 }, splitArea: { areaStyle: { color: ['rgba(0,212,255,0.03)', 'rgba(0,212,255,0.07)'] } }, axisLine: { lineStyle: { color: 'rgba(0,212,255,0.2)' } }, splitLine: { lineStyle: { color: 'rgba(0,212,255,0.12)' } } },
      series: [{ type: 'radar', data: [ { value: lrVals, name: '线性回归', areaStyle: { color: 'rgba(77,158,255,0.35)' }, lineStyle: { color: '#4d9eff', width: 2.5 }, itemStyle: { color: '#4d9eff', borderWidth: 2, borderColor: '#fff' }, symbolSize: 6 }, { value: rfVals, name: '随机森林', areaStyle: { color: 'rgba(0,230,118,0.35)' }, lineStyle: { color: '#00e676', width: 2.5 }, itemStyle: { color: '#00e676', borderWidth: 2, borderColor: '#fff' }, symbolSize: 6 } ] }]
    });
  } catch(e) { console.warn('Radar chart error:', e); }
}

var FEAT_CN_MAP = {"city": "城市", "work_year": "工作经验", "education": "学历", "com_type": "企业类型", "com_size": "企业规模"};
var FEAT_DESC_MAP = { work_year: '工作经验越丰富，薪资水平越高，是影响薪资的最重要因素', com_size: '大型企业往往能提供更高的薪资水平', city: '不同城市的经济发展水平直接影响薪资差异', com_type: '互联网、金融等行业薪资水平明显高于其他行业', education: '高学历往往意味着更高的薪资起点' };
var FEAT_COLORS = { work_year: {s:'#00e676',e:'#00c853'}, com_size: {s:'#4d9eff',e:'#2979ff'}, city: {s:'#00d4ff',e:'#00b0ff'}, com_type: {s:'#ff9100',e:'#ff6d00'}, education: {s:'#b388ff',e:'#7c4dff'} };

function renderFeatureImportance(features) {
  if (typeof echarts === 'undefined') return;
  var dom = document.getElementById('chart-feature-importance');
  if (!dom) return;
  if (charts['feature-importance']) { charts['feature-importance'].dispose(); delete charts['feature-importance']; }
  try {
    var chart = echarts.init(dom); charts['feature-importance'] = chart;
    var skeleton = dom.querySelector('.chart-skeleton'); if (skeleton) skeleton.style.display = 'none';

    var sorted = features.slice().sort(function(a,b){ return b.importance - a.importance; });
    var top = sorted[0];

    if (top) {
      var topName = FEAT_CN_MAP[top.feature] || top.feature;
      var topPct = (top.importance * 100).toFixed(1);
      var finder = document.getElementById('feat-top-finder');
      if (finder) {
        finder.innerHTML = '💡 <strong>' + topName + '</strong> 对薪资影响最大，权重达到 <strong style="color:var(--accent-cyan);font-size:18px;">' + topPct + '%</strong>，' + (FEAT_DESC_MAP[top.feature] || '是薪资预测的核心指标');
      }
    }

    var barData = sorted.map(function(f) {
      var cs = FEAT_COLORS[f.feature] || {s:'#b388ff',e:'#00d4ff'};
      return { value: f.importance, itemStyle: { color: new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:cs.s},{offset:1,color:cs.e}]), borderRadius: [0,6,6,0] } };
    });

    chart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, backgroundColor: 'rgba(15,31,58,0.95)', borderColor: 'rgba(0,212,255,0.2)', borderWidth: 1, textStyle: { color:'#e6f1ff', fontSize:13 }, formatter: function(params) { var p=params[0]; var feat = sorted[p.dataIndex].feature; var cn = FEAT_CN_MAP[feat]||feat; var v=(p.value*100).toFixed(1); var desc=FEAT_DESC_MAP[feat]||''; return '<div style="font-weight:600;font-size:15px;margin-bottom:4px;">'+cn+'</div><div style="color:var(--accent-cyan);font-size:18px;font-weight:700;margin:4px 0;">'+v+'%</div><div style="font-size:12px;color:#8892b0;border-top:1px solid rgba(0,212,255,0.1);padding-top:4px;">影响权重</div>'+(desc?'<div style="font-size:12px;color:#8892b0;margin-top:2px;">'+desc+'</div>':''); } },
      grid: { left: '3%', right: '15%', bottom: '3%', containLabel: true },
      xAxis: { show: false, type: 'value', max: 1 },
      yAxis: { type: 'category', data: sorted.map(function(f){ return FEAT_CN_MAP[f.feature]||f.feature; }), axisLabel: { color:'#e6f1ff', fontSize:13, fontWeight:500 }, axisLine: { show:false }, axisTick: { show:false }, splitLine: { show:false } },
      series: [
        { type: 'bar', barWidth: '60%', barGap: '-100%', data: sorted.map(function(){ return {value:1,itemStyle:{color:'rgba(255,255,255,0.04)',borderRadius:[0,6,6,0]}}; }), z:0, silent: true, animation: false },
        { type: 'bar', barWidth: '60%', data: barData, z:1, label: { show:true, position:'right', formatter: function(p){return (p.value*100).toFixed(1)+'%';}, color:'#8892b0', fontSize:13, fontWeight:600 }, animationDuration:1000, animationEasing:'elasticOut' }
      ]
    });
  } catch(e) { console.warn('Feature importance chart error:', e); }
}

function scrollChatBottom() {
  var el = document.getElementById('chat-messages');
  if (el) { setTimeout(function(){ el.scrollTop = el.scrollHeight; }, 100); }
}

function addChatMessage(role, content) {
  var msg = document.getElementById('chat-messages');
  if (!msg) return;
  var isUser = role === 'user';
  var avatar = isUser ? '👤' : '🤖';
  var html = content.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g,'<br>').replace(/\`\`\`(\w*)\n?([\s\S]*?)\`\`\`/g,'<pre><code>$2</code></pre>').replace(/\`([^\`]+)\`/g,'<code>$1</code>').replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>').replace(/\*([^*]+)\*/g,'<em>$1</em>');
  var div = document.createElement('div'); div.className = 'chat-msg ' + (isUser?'user':'bot');
  div.innerHTML = '<div class="chat-avatar">'+avatar+'</div><div class="chat-bubble">'+html+'</div>';
  msg.appendChild(div); scrollChatBottom();
}

function addTypingIndicator() {
  var msg = document.getElementById('chat-messages');
  if (!msg) return;
  var div = document.createElement('div'); div.className = 'chat-typing'; div.id = 'typing-indicator';
  div.innerHTML = '<div class="chat-avatar">🤖</div><div class="typing-dots"><span></span><span></span><span></span></div>';
  msg.appendChild(div); scrollChatBottom();
}

function removeTypingIndicator() { var el = document.getElementById('typing-indicator'); if (el) el.remove(); }

function setChatStatus(text, color) {
  var el = document.getElementById('chat-status');
  if (el) { el.textContent = text; if (color) el.style.color = color; }
}

function sendChat() {
  if (isChatting) return;
  var input = document.getElementById('chat-input'); var btn = document.getElementById('chat-send-btn');
  if (!input || !btn) return;
  var msg = input.value.trim(); if (!msg) return;
  isChatting = true; btn.disabled = true;
  addChatMessage('user', msg); input.value = ''; input.style.height = 'auto';
  addTypingIndicator(); setChatStatus('⏳ Thinking...', 'var(--accent-orange)');
  fetch('/api/chat', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message:msg, session_id:CHAT_SESSION}) })
  .then(function(r){return r.json();}).then(function(data){
    removeTypingIndicator();
    if (data.error) { addChatMessage('bot', '⚠ '+data.error); setChatStatus('⚠ Error', 'var(--accent-red)'); }
    else { addChatMessage('bot', data.reply); setChatStatus('🟢 Ready'); }
    isChatting = false; btn.disabled = false; input.focus();
  }).catch(function(err){
    removeTypingIndicator(); addChatMessage('bot', '⚠ Request failed: '+err.message);
    setChatStatus('⚠ Error', 'var(--accent-red)'); isChatting = false; btn.disabled = false; input.focus();
  });
}

function handleChatKey(e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChat(); } }

function clearChat() {
  fetch('/api/chat/clear', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({session_id:CHAT_SESSION}) })
  .then(function(){
    var msg = document.getElementById('chat-messages');
    if (msg) msg.innerHTML = '<div class="chat-msg bot"><div class="chat-avatar">🤖</div><div class="chat-bubble"><p>Chat cleared. Ask me anything!</p></div></div>';
    setChatStatus('🟢 Ready');
  }).catch(function(e){ console.warn('Clear chat error:', e.message); });
}

document.addEventListener('DOMContentLoaded', function() {
  loadAllCharts();
  var input = document.getElementById('chat-input');
  if (input) {
    input.addEventListener('input', function() { this.style.height = 'auto'; this.style.height = Math.min(this.scrollHeight, 120) + 'px'; });
  }
});
