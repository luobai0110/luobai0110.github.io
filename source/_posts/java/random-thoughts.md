---
title: 炸鸡
date: 2024-12-20 08:45:35
category: 
  - 炸鸡
tag:
  - cs基础
  - java
---

## 数组相关

### 为什么数组的索引通常从0开始

因为索引实际上表示偏移量, 从0开始能够很好的反应数组元素和数组第一个元素的偏移量

## 补码, 原码, 补码

- 原码: 实数的二进制表示,

  **规则**: 第一位表示符号, 正数的符号为0, 负数的符号为1

  **优点**: 简单易读, 符合人类直觉

  **缺点**: 对负数在计算机内的表达不友好

- 反码: 解决如何在计算机中有效地表示和处理负数，特别是避免在二进制加法运算中出现额外的复杂性.

  **规则**: 正数的反码是其本身; 负数的反码是除符号位取反, 这种编码模式下0有**两种表示**

  0反码的两种表示, 以八位示例

  ```bash
  正数0: 
  	原码: 0000 0000
  	反码: 0000 0000
  负数0: 
  	原码: 1000 0000
  	反码: 1111 1111
  ```

  **缺点:**

  - **0有两种表达方式**,: 需要花费额外的资源区判断0
  - **加法需要额外的处理**：在进行加法运算时，如果结果超出范围，需要额外处理进位（循环进位）。

- 补码: 补码是反码的升级版本 ,补码是目前计算机中最常用的负数表示法. 

  **规则**: 正数的补码是其本身, 负数的补码是其反码加1

  **优点**: 只有一个零，避免了反码中的“+0”和“-0”问题, 加法运算可以直接使用二进制加法器进行计算，不需要特别处理符号位或进位。

## 常见函数式接口的用途

在Java中，函数式接口（Functional Interface）是指只有一个抽象方法的接口。Java 8引入了函数式编程的特性，并提供了一些常见的函数式接口，这些接口通常用于支持Lambda表达式和方法引用。以下是一些常见的函数式接口及其一般用途：

1. **`java.util.function.Consumer<T>`**

- **用途**: 表示接受一个输入参数并且不返回结果的操作。
- **方法**: `void accept(T t)`
- **示例**: 用于遍历集合、打印日志、执行副作用操作等。

```java
Consumer<String> print = s -> System.out.println(s);
print.accept("Hello, World!");
```

2. **`java.util.function.Supplier<T>`**

- **用途**: 表示不接受参数但返回一个结果的操作。
- **方法**: `T get()`
- **示例**: 用于延迟计算、工厂方法、生成随机数等。

```java
Supplier<Double> randomValue = () -> Math.random();
System.out.println(randomValue.get());
```

3. **`java.util.function.Function<T, R>`**

- **用途**: 表示接受一个输入参数并返回一个结果的操作。
- **方法**: `R apply(T t)`
- **示例**: 用于转换数据类型、映射操作等。

```java
Function<String, Integer> stringLength = s -> s.length();
System.out.println(stringLength.apply("Hello"));
```

4. **`java.util.function.Predicate<T>`**

- **用途**: 表示一个布尔值函数，接受一个输入参数并返回一个布尔值。
- **方法**: `boolean test(T t)`
- **示例**: 用于过滤集合、条件判断等。

```java
Predicate<Integer> isEven = n -> n % 2 == 0;
System.out.println(isEven.test(4));
```

5. **`java.util.function.UnaryOperator<T>`**

- **用途**: 表示对一个操作数进行操作并返回相同类型的结果。
- **方法**: `T apply(T t)`
- **示例**: 用于对集合中的元素进行相同的操作。

```java
UnaryOperator<Integer> square = n -> n * n;
System.out.println(square.apply(5));
```

6. **`java.util.function.BinaryOperator<T>`**

- **用途**: 表示对两个相同类型的操作数进行操作并返回相同类型的结果。
- **方法**: `T apply(T t1, T t2)`
- **示例**: 用于对两个元素进行操作，如求和、求积等。

```java
BinaryOperator<Integer> sum = (a, b) -> a + b;
System.out.println(sum.apply(3, 4));
```

7. **`java.util.function.BiFunction<T, U, R>`**

- **用途**: 表示接受两个输入参数并返回一个结果的操作。
- **方法**: `R apply(T t, U u)`
- **示例**: 用于处理两个不同类型的输入并返回结果。

```java
BiFunction<Integer, Integer, Integer> multiply = (a, b) -> a * b;
System.out.println(multiply.apply(3, 4));
```

8. **`java.util.function.BiConsumer<T, U>`**

- **用途**: 表示接受两个输入参数并且不返回结果的操作。
- **方法**: `void accept(T t, U u)`
- **示例**: 用于处理两个不同类型的输入并执行操作。

```java
BiConsumer<String, Integer> printKeyValue = (key, value) -> System.out.println(key + ": " + value);
printKeyValue.accept("age", 30);
```

9. **`java.util.function.BiPredicate<T, U>`**

- **用途**: 表示一个布尔值函数，接受两个输入参数并返回一个布尔值。
- **方法**: `boolean test(T t, U u)`
- **示例**: 用于处理两个不同类型的输入并进行条件判断。

```java
BiPredicate<String, Integer> isLengthGreaterThan = (s, length) -> s.length() > length;
System.out.println(isLengthGreaterThan.test("Hello", 3));
```

10. **`java.util.function.IntFunction<R>`**

- **用途**: 表示接受一个`int`类型参数并返回一个结果的操作。
- **方法**: `R apply(int value)`
- **示例**: 用于处理`int`类型的输入并返回结果。

```java
IntFunction<String> intToString = i -> Integer.toString(i);
System.out.println(intToString.apply(123));
```

11. **`java.util.function.ToIntFunction<T>`**

- **用途**: 表示接受一个输入参数并返回一个`int`类型结果的操作。
- **方法**: `int applyAsInt(T value)`
- **示例**: 用于将输入转换为`int`类型。

```java
ToIntFunction<String> stringToInt = s -> Integer.parseInt(s);
System.out.println(stringToInt.applyAsInt("123"));
```

12. `java.util.function.ToIntBiFunction<T, U>`

- **用途**: 表示接受两个输入参数并返回一个`int`类型结果的操作。
- **方法**: `int applyAsInt(T t, U u)`
- **示例**: 用于处理两个不同类型的输入并返回`int`类型结果。

```java
ToIntBiFunction<String, String> sumLengths = (s1, s2) -> s1.length() + s2.length();
System.out.println(sumLengths.applyAsInt("Hello", "World"));
```

13. **`java.util.function.IntConsumer`**

- **用途**: 表示接受一个`int`类型参数并且不返回结果的操作。
- **方法**: `void accept(int value)`
- **示例**: 用于处理`int`类型的输入并执行操作。

```java
IntConsumer printInt = i -> System.out.println(i);
printInt.accept(123);
```

14. **`java.util.function.IntSupplier`**

- **用途**: 表示不接受参数但返回一个`int`类型结果的操作。
- **方法**: `int getAsInt()`
- **示例**: 用于生成`int`类型的随机数或常量。

```java
IntSupplier randomInt = () -> (int) (Math.random() * 100);
System.out.println(randomInt.getAsInt());
```

15. **`java.util.function.IntPredicate`**

- **用途**: 表示一个布尔值函数，接受一个`int`类型参数并返回一个布尔值。
- **方法**: `boolean test(int value)`
- **示例**: 用于对`int`类型的输入进行条件判断。

```java
IntPredicate isEven = i -> i % 2 == 0;
System.out.println(isEven.test(4));
```

这些函数式接口为Java中的函数式编程提供了强大的支持，使得代码更加简洁和灵活。通过使用这些接口，开发者可以更容易地编写可读性高、易于维护的代码。

## switch和if的效率

1. if会根据代码顺序从前之后的匹配
2. switch会根据case后的值进行正序排序， 之后使用二分查找进行匹配，因此在离散值的情况下，switch效率更高

## 浅拷贝和深拷贝的实现方式

### 浅拷贝

浅拷贝是指复制对象时，仅复制对象的基本类型字段和对象引用类型的**引用地址**，而不会复制引用类型的实际内容。

#### 实现示例，通过实现 `Cloneable` 接口并重写 `clone` 方法

```java
class Person implements Cloneable {
    String name;
    int age;
    Address address;

    public Person(String name, int age, Address address) {
        this.name = name;
        this.age = age;
        this.address = address;
    }

    @Override
    protected Object clone() throws CloneNotSupportedException {
        return super.clone();
    }
}

class Address {
    String city;

    public Address(String city) {
        this.city = city;
    }
}

public class Main {
    public static void main(String[] args) throws CloneNotSupportedException {
        Address address = new Address("New York");
        Person person1 = new Person("John", 30, address);
        Person person2 = (Person) person1.clone();

        System.out.println(person1 == person2); // false
        System.out.println(person1.address == person2.address); // true (浅拷贝)
    }
}
```

### 深拷贝(保护性拷贝)

深拷贝是指复制对象时，不仅复制对象的基本类型字段，还会递归复制引用类型的实际内容，使得新对象与原对象完全独立

#### 实现方式，通过序列化

```java
import java.io.*;

class Person implements Serializable {
    String name;
    int age;
    Address address;

    public Person(String name, int age, Address address) {
        this.name = name;
        this.age = age;
        this.address = address;
    }
}

class Address implements Serializable {
    String city;

    public Address(String city) {
        this.city = city;
    }
}

public class Main {
    public static void main(String[] args) throws IOException, ClassNotFoundException {
        Address address = new Address("New York");
        Person person1 = new Person("John", 30, address);

        // 深拷贝
        ByteArrayOutputStream byteOut = new ByteArrayOutputStream();
        ObjectOutputStream out = new ObjectOutputStream(byteOut);
        out.writeObject(person1);

        ByteArrayInputStream byteIn = new ByteArrayInputStream(byteOut.toByteArray());
        ObjectInputStream in = new ObjectInputStream(byteIn);
        Person person2 = (Person) in.readObject();

        System.out.println(person1 == person2); // false
        System.out.println(person1.address == person2.address); // false (深拷贝)
    }
}
```

在 Java 中，实现浅拷贝和深拷贝的方法如下：

------

### **浅拷贝**

浅拷贝是指复制对象时，仅复制对象的基本类型字段和对象引用类型的引用地址，而不会复制引用类型的实际内容。

#### **实现方式 1：实现 `Cloneable` 接口并重写 `clone` 方法**

```java
class Person implements Cloneable {
    String name;
    int age;
    Address address;

    public Person(String name, int age, Address address) {
        this.name = name;
        this.age = age;
        this.address = address;
    }

    @Override
    protected Object clone() throws CloneNotSupportedException {
        return super.clone();
    }
}

class Address {
    String city;

    public Address(String city) {
        this.city = city;
    }
}

public class Main {
    public static void main(String[] args) throws CloneNotSupportedException {
        Address address = new Address("New York");
        Person person1 = new Person("John", 30, address);
        Person person2 = (Person) person1.clone();

        System.out.println(person1 == person2); // false
        System.out.println(person1.address == person2.address); // true (浅拷贝)
    }
}
```

------

### **深拷贝**

深拷贝是指复制对象时，不仅复制对象的基本类型字段，还会递归复制引用类型的实际内容，使得新对象与原对象完全独立。

#### **实现方式 1：手动复制所有字段**

```java
class Person {
    String name;
    int age;
    Address address;

    public Person(String name, int age, Address address) {
        this.name = name;
        this.age = age;
        this.address = address;
    }

    public Person deepCopy() {
        Address newAddress = new Address(this.address.city); // 深拷贝 Address
        return new Person(this.name, this.age, newAddress);
    }
}
```

#### **实现方式 2：使用序列化**

通过对象序列化和反序列化实现深拷贝：

```java
import java.io.*;

class Person implements Serializable {
    String name;
    int age;
    Address address;

    public Person(String name, int age, Address address) {
        this.name = name;
        this.age = age;
        this.address = address;
    }
}

class Address implements Serializable {
    String city;

    public Address(String city) {
        this.city = city;
    }
}

public class Main {
    public static void main(String[] args) throws IOException, ClassNotFoundException {
        Address address = new Address("New York");
        Person person1 = new Person("John", 30, address);

        // 深拷贝
        ByteArrayOutputStream byteOut = new ByteArrayOutputStream();
        ObjectOutputStream out = new ObjectOutputStream(byteOut);
        out.writeObject(person1);

        ByteArrayInputStream byteIn = new ByteArrayInputStream(byteOut.toByteArray());
        ObjectInputStream in = new ObjectInputStream(byteIn);
        Person person2 = (Person) in.readObject();

        System.out.println(person1 == person2); // false
        System.out.println(person1.address == person2.address); // false (深拷贝)
    }
}
```

#### **实现方式 3：使用第三方工具**

例如，使用 Apache Commons Lang 提供的 `SerializationUtils`：

```java
import org.apache.commons.lang3.SerializationUtils;

class Person implements Serializable {
    String name;
    int age;
    Address address;

    public Person(String name, int age, Address address) {
        this.name = name;
        this.age = age;
        this.address = address;
    }
}

class Address implements Serializable {
    String city;

    public Address(String city) {
        this.city = city;
    }
}

public class Main {
    public static void main(String[] args) {
        Address address = new Address("New York");
        Person person1 = new Person("John", 30, address);

        // 深拷贝
        Person person2 = SerializationUtils.clone(person1);

        System.out.println(person1 == person2); // false
        System.out.println(person1.address == person2.address); // false (深拷贝)
    }
}
```

------

### **总结**

| 方法           | 浅拷贝                           | 深拷贝                 |
| -------------- | -------------------------------- | ---------------------- |
| **实现简单性** | 简单，效率高                     | 较复杂，可能涉及递归   |
| **数据独立性** | 复制后部分数据共享（引用类型）   | 复制后完全独立         |
| **适用场景**   | 适合不需要修改引用类型数据的场景 | 需要对象完全独立时使用 |

## java的四种引用类型





## hashmap的键一般是不可变对象，即被final修饰的类，例如String，Integer等
