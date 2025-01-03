---
title: 简单排序算法
date: 2024-12-18 11:50:32
category:
  - 算法
tag:
  - 排序算法
  - 算法
---

# 简单算法

## 排序算法

### 冒泡排序

#### 原理

基于重复遍历待排序的元素，比较相邻的元素并交换它们的位置，直到整个序列有序。通过不断将较大的元素“冒泡”到序列的末端，直到所有元素都按顺序排列。时间复杂度为O(n<sup>2</sup>)，空间复杂度O(1)

#### 演示

![](https://raw.githubusercontent.com/luobai0110/blogpic/main/bubbleSort.gif)

#### 代码

```java
public static void bubbleSort(int[] arr) {
    if (arr == null || arr.length <= 1) {
        return;
    }
    // 外层循环, 迭代次数为数组的长度
    for (int i = 0; i < arr.length - 1; i++) {
        // 内层循环, 迭代次数为未排序元素个数减一
        for (int j = 0; j < arr.length - i - 1; j++) {
            // 升序排序
            if (arr[j] > arr[j + 1]) {
                // 交换位置
                int temp = arr[j + 1];
                arr[j + 1] = arr[j];
                arr[j] = temp;
            }
        }
    }
}
```

### 选择排序

#### 原理

首先在未排序序列中找到最小（大）元素，存放到排序序列的起始位置。然后，再从剩余未排序元素中
继续寻找最小（大）元素，然后放到已排序序列的末尾。以此类推，直到所有元素均排序完毕。
时间复杂度O(n²), 空间复杂度O(1)

#### 演示

![selectionSort](https://raw.githubusercontent.com/luobai0110/blogpic/main/selectionSort.gif)

#### 代码

```java
public static void selectSort(int[] arr) {
    // 数组长度小于等于 1 或者数组为null时, 不进行排序
    if (arr == null || arr.length <= 1) {
        return;
    }
    for (int i = 0; i < arr.length - 1; i++) {
        int maxIndex = i;
        // 找到此次循环的最大值的索引
        for (int j = i + 1; j < arr.length; j++) {
            if (arr[j] < arr[maxIndex]) {
                maxIndex = j;
            }
        }
        // 在内层循环外交换数据, 减少交换次数
        if (maxIndex != i) {
            int t = arr[maxIndex];
            arr[maxIndex] = arr[i];
            arr[i] = t;
        }
    }
}
```

### 插入排序

#### 原理

通过构建有序序列，对于未排序数据，在已排序序列中从后向前扫描，找到相应位置并插入。插入排序在实现上，通常采用in-place排序O(1)的额外空间的排序），因而在从后向前扫描过程中，需要反复把已排序元素逐步向后挪位，为最新元素提供插入空间。时间复杂度O(n²), 空间复杂度O(1), 最好情况O(n)

![insertionSort](https://raw.githubusercontent.com/luobai0110/blogpic/main/insertionSort.gif)

#### 代码

```java
public static void insertSort(int[] arr) {
    // 不需要排序的数组直接返回
    if (arr == null || arr.length <= 1) {
        return;
    }
    for (int i = 1; i < arr.length; i++) {
        // 取出当前需要排序的值
        int currentNums = arr[i];
        int j = i - 1;
        // 倒序比较已经排序好的值, 一直到当前值大于某个值或者索引为0;
        while (j >= 0 && currentNums < arr[j]) {
            arr[j + 1] = arr[j];
            // 注意, 如果此刻退出循环, 索引比需要插入的值小1
            j--;
        }
        arr[j + 1] = currentNums;
    }
}
```

### 归并排序



