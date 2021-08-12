package exercise21;

import org.testng.annotations.Test;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.AfterMethod;

public class TestClass02 {
	
  @Test(priority=1)
  public void tMethod3() {
	  System.out.println("method03");
  }
  @Test(priority=2)
  public void tMethod4() {
	  System.out.println("method04");
  }
  @BeforeMethod
  public void beforeMethod() {
  }

  @AfterMethod
  public void afterMethod() {
  }

}
