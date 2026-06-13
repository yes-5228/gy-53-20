<script setup>
import { onMounted, reactive, ref } from "vue";
import { parkingApi } from "../api/parking";
import StatusBadge from "../components/StatusBadge.vue";

const blacklist = ref([]);
const message = ref("");
const form = reactive({
  plate_number: "",
  reason: "欠费",
  remark: "",
});

const reasonOptions = ["欠费", "违规", "其他"];

async function loadBlacklist() {
  const data = await parkingApi.getBlacklist();
  blacklist.value = data.items;
}

async function addItem() {
  message.value = "";
  try {
    await parkingApi.addBlacklist({
      plate_number: form.plate_number,
      reason: form.reason,
      remark: form.remark,
    });
    form.plate_number = "";
    form.remark = "";
    await loadBlacklist();
    message.value = "添加成功";
  } catch (err) {
    message.value = err.message;
  }
}

async function toggleStatus(item) {
  const newStatus = item.status === "active" ? "removed" : "active";
  await parkingApi.updateBlacklist(item.id, { status: newStatus });
  await loadBlacklist();
}

async function removeItem(item) {
  if (!confirm(`确定要删除车牌 ${item.plate_number} 的黑名单记录吗？`)) return;
  await parkingApi.deleteBlacklist(item.id);
  await loadBlacklist();
}

onMounted(loadBlacklist);
</script>

<template>
  <div class="page-stack">
    <header class="page-header">
      <div>
        <h2>黑名单管理</h2>
        <p>管理欠费、违规等禁止入场的车辆。</p>
      </div>
    </header>

    <div class="two-column" style="display: grid;">
      <form class="form-panel" @submit.prevent="addItem">
        <h3>添加黑名单</h3>
        <label>车牌号<input v-model="form.plate_number" required placeholder="例如：沪A12345" /></label>
        <label>
          原因
          <select v-model="form.reason">
            <option v-for="opt in reasonOptions" :key="opt" :value="opt">{{ opt }}</option>
          </select>
        </label>
        <label>备注<input v-model="form.remark" placeholder="选填" /></label>
        <button class="primary-button" type="submit">加入黑名单</button>
        <p v-if="message" class="hint-text">{{ message }}</p>
      </form>

      <section class="table-section">
        <h3>黑名单列表</h3>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>车牌</th>
                <th>原因</th>
                <th>状态</th>
                <th>添加时间</th>
                <th>备注</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in blacklist" :key="item.id">
                <td>{{ item.plate_number }}</td>
                <td>{{ item.reason }}</td>
                <td><StatusBadge :status="item.status" /></td>
                <td>{{ item.created_at }}</td>
                <td>{{ item.remark || "-" }}</td>
                <td>
                  <button class="small-button" type="button" @click="toggleStatus(item)">
                    {{ item.status === "active" ? "解除" : "启用" }}
                  </button>
                  <button class="small-button" type="button" style="margin-left: 6px; background: #e07060; color: #fff;" @click="removeItem(item)">
                    删除
                  </button>
                </td>
              </tr>
              <tr v-if="blacklist.length === 0">
                <td colspan="6" style="text-align: center; color: #999;">暂无黑名单记录</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </div>
</template>
