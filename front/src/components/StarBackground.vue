<template>
    <div class="animate-box">
        <div class="layer1"></div>
        <div class="layer2"></div>
        <div class="layer3"></div>
        <div class="layer4"></div>
        <div class="layer5"></div>
        <div class="title">Sass 星空</div>
    </div>
</template>
<script lang="ts" setup>

</script>
<style lang="scss" scoped>
@use "sass:math";
@use "sass:string";

.animate-box {
    position: absolute;
    left: 0;
}

.title {
    -webkit-background-clip: text;
    color: transparent;
}

@function star($n) {
    $result : '#{math.random(100)}vw #{math.random(100)}vh #fff';

    @for $i from 2 through $n {
        $result: '#{$result},#{math.random(100)}vw #{math.random(100)}vh #fff'
    }

    @return string.unquote($result);
}

// 层级数量
$n: 5;
// 移动时间
$duration: 300s;
//数量
$count: 150;

@for $i from 1 through $n {

    .layer#{$i} {
        position: fixed;
        width: #{$i}px;
        height: #{$i}px;
        border-radius: 50%;
        box-shadow: star($count);
        animation: moveup #{$duration} linear infinite;
        z-index: -5;
        pointer-events: none;
    }

    .layer#{$i}::after {
        content: '';
        position: inherit;
        width: inherit;
        height: inherit;
        border-radius: inherit;
        box-shadow: inherit;
        left: 0;
        top: 100vh;
    }

    $duration: math.floor(math.div($duration , 2));
    $count: math.floor(math.div($count , 2));
}

;

@keyframes moveup {
    to {
        transform: translateY(-100vh);
    }
}
</style>