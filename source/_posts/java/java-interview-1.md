---
title: java基础面试一
date: 2024-12-17 21:09:22
category: 
  - java
tag: 
  - java
  - 面试
---

## **String相关**

### **为什么不建议的循环中使用**`+`**拼接字符串**

#### `+`**的内部实现原理**

使用`+`操作字符串时,`java`在编译时调用`StringBuilder`的`append`方法去拼接字符串

实现如下：

```
str = new StringBuilder(str).append("text").toString();
```

如果在循环中使用则会在每次循环中创建`StringBuilder`对象, 造成性能和内存的损失, 而如果在循环创建`StirngBuilder`对象然后再循环中调用`append`方法这可以避免该问题

以100000次循环为例:

使用`+`拼接字符串

```
public static void main(String[] args) {
    int count = 100000;
    String str = "";
    long start = System.currentTimeMillis();
    for (int i = 0; i < count; i++) {
        str = str + i;
    }
    long end = System.currentTimeMillis() - start;
    System.out.println("String: " + end + " ms");
}
```

运行结果:

![img](https://raw.githubusercontent.com/luobai0110/blogpic/main/image-20241206201809924.png)

使用StringBuilder:

```
 public static void main(String[] args) {
        int count = 100000;
        StringBuilder sb = new StringBuilder();
        long start = System.currentTimeMillis();
        for (int i = 0; i < count; i++) {
            sb.append(i);
        }
        long end = System.currentTimeMillis() - start;
        System.out.println("String: " + end + " ms");
}
```

运行结果:

![img](https://raw.githubusercontent.com/luobai0110/blogpic/main/image-20241206201650175.png)

##### **相关, 为什么String不可变**

打开String原码可以发现![image-20241206205550646](https://raw.githubusercontent.com/luobai0110/blogpic/main/image-20241206205550646.png)

java使用byte数组存储字符串(java9 之前使用char数组), 可以看到**value**被**final**修饰, 这代表**value**的值不可改变,

但注意, 这并不代表这是String不可改变的原因, 我们有如下代码:

```
public static void main(String[] args) {
    final int[] value = {1, 2, 3, 4};
    int[] another = {1, 3, 4, 8};
//        value = another; //  报错, final不可变
    System.out.println(Arrays.toString(value));
    value[1] = 3; // value[1]发生改变, 但value并未发生, 即value指向的位置并未发生改变
    System.out.println(Arrays.toString(value));
}
```

被final修饰的数组value其值不可改变, 仅仅值value指向的地址不发生改变, 但是存储在堆中的数组的内容确实可以发生更改的, 这意味着如果我们可以直接修改String中 `value`数组中某个所以位置的值, 进而影响字符串的内容;

所以, `String`不可变的原因应该是, `value`同时被`private`和`final`修饰, 这保证了`value`的内容不会被外界改变, 同时, `String` 被`final`修饰, 这保证了不会通过子类的改变value的值

## Object相关

### `equals和==`**的区别**

1. `==`对于基本数据类型是比较值是否相等，相等为true，反之为false

   ```
   int a = 1;
   int b = 1;
   System.out.println(a == b);
   ```

   输出：

   ![image-20241208154551284](https://raw.githubusercontent.com/luobai0110/blogpic/main/image-20241208154551284.png)

   对于引用数据类型，==比较的则是二者的地址值，相同为true

   ```
   String str1 = new String("hello");
   String str2 = new String("hello");
   System.out.println(str1 == str2);
   ```

   输出：

   ![image-20241208155114707](https://raw.githubusercontent.com/luobai0110/blogpic/main/image-20241208155114707.png)

2. equals使用Object提供的一个方法，其源码如下：

   ```
   public boolean equals(Object obj) {
       return (this == obj);
   }
   ```

   可以看到，如果我们为重写equals方法，则其实现的内部机制是==，即比较地址值。

   所以，一般情况下我们会重写equals方法来达到比较对象的内容是否相等的功能；但需要注意的是，equals方法的具体功能最终还是要看其内部实现逻辑。

3. 特殊情况

   对于字符串对象，由于存在字符串常量池的情况，如果是使用字面量创建对象，则会指向内存中相同的位置。

   ```
   String str1 = "hello";  // 直接使用字面量，会被存储在字符串常量池中
   String str2 = "hello";  // 引用同一个常量池中的对象
   System.out.println(str1 == str2);  // 输出 true，因为它们指向同一个对象
   ```

   ![image-20241208160255652](https://raw.githubusercontent.com/luobai0110/blogpic/main/image-20241208160255652.png)

   对于包装类对象，如果值的范围在包装类缓存值的范围内，那么也会指向内存中同一个地址位置。

### **重载和重写的区别**

1. 重写(Override): 指子类定义了一个与其父类中具有相同名称、参数列表和返回类型的方法，并且子类方法的实现覆盖了父类方法的实现。 **注意事项**：

   - 重写的方法不能抛出新的检查异常或者子类不能抛出比重写的方法更加宽泛的异常；
   - 重写的方法可以抛出任何运行时异常；
     - 重写的方法的访问权限不能比被重写的方法的访问权限更低；
   - 重写的方法返回值可以与被重写的方法不同，但必须是被重写的方法返回值的派生类。

2. 重载(Overload): **同一个类中或继承关系**中的父类与子类中，方法名相同但参数列表不同的情况。

   **注意事项**：

   - 返回值不同不算重载；
   - 重载方法可以改变访问修饰符；
   - 重载方法可以抛出新的或者更加宽泛的异常；
   - 被重载的方法必须改变参数列表

## **Integer**

### **integer的缓存机制**

我们可以通过一下代码判断java是否存在缓存机制：

```
public static void main(String[] args) {
    Integer i = 128;
    Integer i1 = 128;
    System.out.println(i == i1); // false
    System.out.println(i.equals(i1)); //false
    i = 128;
    i1 = 128;
    System.out.println(i == i1); // true
    System.out.println(i.equals(i1)); //true
}

```

输出：

![image-20241208150145484](https://raw.githubusercontent.com/luobai0110/blogpic/main/image-20241208150145484.png)

Integer的缓存是从java5引用的一个有助于节省内存、提高性能的特性， 在jvm初始化的时候会将[-128, 128)区间的数字存入内存， 如果初始化的integer对象的内容处在这个区间之间则不会新建对象，而是从内存中直接取出。

![image-20241208145738908](https://raw.githubusercontent.com/luobai0110/blogpic/main/image-20241208145738908.png)

```
/**
 * Cache to support the object identity semantics of autoboxing for values between
 * -128 and 127 (inclusive) as required by JLS.
 *
 * The cache is initialized on first usage.  The size of the cache
     * may be controlled by the {@code -XX:AutoBoxCacheMax=<size>} option.
 * During VM initialization, java.lang.Integer.IntegerCache.high property
 * may be set and saved in the private system properties in the
 * sun.misc.VM class.
 */

private static class IntegerCache {
    static final int low = -128;
    static final int high;
    static final Integer cache[];

    static {
        // high value may be configured by property
        int h = 127;
        String integerCacheHighPropValue =
            sun.misc.VM.getSavedProperty("java.lang.Integer.IntegerCache.high");
        if (integerCacheHighPropValue != null) {
            try {
                int i = parseInt(integerCacheHighPropValue);
                i = Math.max(i, 127);
                // Maximum array size is Integer.MAX_VALUE
                h = Math.min(i, Integer.MAX_VALUE - (-low) -1);
            } catch( NumberFormatException nfe) {
                // If the property cannot be parsed into an int, ignore it.
            }
        }
        high = h;

        cache = new Integer[(high - low) + 1];
        int j = low;
        for(int k = 0; k < cache.length; k++)
            cache[k] = new Integer(j++);

        // range [-128, 127] must be interned (JLS7 5.1.7)
        assert IntegerCache.high >= 127;
    }

    private IntegerCache() {}
}
```

通过javadoc可知， 我们可以通过`AutoBoxCacheMax==size`参数来指定初始化最大值的范围。

> 此机制还存在与Byte、Long、Short、Character， 对于前三者其缓存区间与Integer相同()，而后者缓存范围在[0, 127] (ASCII码的取值范围)。

## IO

### 普通IO和BufferedIO有速度差距的原因

![0ffabbf8654d67bbc092417c98a772b](https://raw.githubusercontent.com/luobai0110/blogpic/main/0ffabbf8654d67bbc092417c98a772b.png)

虽然使用普通io时指定了Byte数组的大小, 但是普通io的底层仍然是按照一个一个字节读取的

![dabe5c9b66df0ab5e0182ad0dca4e03](https://raw.githubusercontent.com/luobai0110/blogpic/main/dabe5c9b66df0ab5e0182ad0dca4e03.png)

使用`bufferedio`时, 会从文件中读取较大的数据块到缓冲区, 减少磁盘的io次数, 从而加快文件的读取写入速度

![image-20241217204404282](https://raw.githubusercontent.com/luobai0110/blogpic/main/image-20241217204404282.png)

### 为什么字节流能够读取所有文件还要设计出字节流

为了解决unicode的读取问题



## 多线程

### 创建线程安全实例的方式

> [] (https://blog.yuanzhou.site/2024/12/20/cs/design-pattern/#%E5%8D%95%E4%BE%8B%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8Fsingleton)

### java的线程状态与操作系统线程状态的区别

